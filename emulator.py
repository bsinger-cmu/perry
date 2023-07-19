import argparse

from AnsibleRunner import AnsibleRunner
from deployment_instance import SimpleInstanceV1, GoalKeeper

import openstack

import time
from datetime import datetime

# Dynamically import modules
import importlib
deployment_instance_module = importlib.import_module('deployment_instance')
defender_module = importlib.import_module('defender')
attacker_module = importlib.import_module('attacker')

from attacker import Attacker, TwoPathAttacker
from defender import WaitAndSpotDefender, Defender

from rich import print as rprint
from console import console, progress
from rich.progress import track
import rich.progress as rpg

from os import path
import yaml
from elasticsearch import Elasticsearch

from colorama import Fore, Style

class Emulator:

    def __init__(self):
        # Initialize connection
        self.openstack_conn = openstack.connect(cloud='default')
        self.scenario = None
        self.config = None
        

    def setup(self, config, scenario, use_snapshots=False, new_flags=False, redeploy_network=True):
        # Setup connection to elasticsearch
        elasticsearch_server = f"https://localhost:{config['elasticsearch']['port']}"
        elasticsearch_api_key = config['elasticsearch']['api_key']

        elasticsearch_conn = Elasticsearch(
            elasticsearch_server,
            basic_auth=("elastic", elasticsearch_api_key),
            verify_certs=False
        )
        # TODO DELETE ALL AGENTS
        # Initialize ansible
        ssh_key_path = config['ssh_key_path']
        ansible_dir = './ansible/'
        ansible_runner = AnsibleRunner(ssh_key_path, None, ansible_dir)

        self.scenario = scenario
        self.config = config

        # Setup attacker
        caldera_api_key = config['caldera']['api_key']
        self.caldera_api_key = caldera_api_key
        attacker_ = getattr(attacker_module, scenario['attacker'])
        self.attacker = attacker_(caldera_api_key)

        # Setup GoalKeeper
        self.goalkeeper = GoalKeeper(self.attacker)
        self.goalkeeper.start_setup_timer()

        # Deploy deployment instance
        deployment_instance_ = getattr(deployment_instance_module, scenario['deployment_instance'])
        self.deployment_instance = deployment_instance_(ansible_runner, self.openstack_conn, config['external_ip'])
        
        # if already_deployed:
        #     self.deployment_instance.load_all_flags()
        # else:
        #     self.deployment_instance.setup(already_deployed=False)
        #     self.deployment_instance.save_all_flags()

        load = self.deployment_instance.setup(use_snapshots=use_snapshots, redeploy_network=redeploy_network, new_flags=new_flags)
        if load == 1: ## Failure to load snapshots
            return load
        
        self.deployment_instance.print_all_flags()

        self.goalkeeper.set_flags(self.deployment_instance.flags)
        self.goalkeeper.set_root_flags(self.deployment_instance.root_flags)

        self.goalkeeper.start_execution_timer()
        
        # Setup initial defender
        defender_ = getattr(defender_module, scenario['defender']['type'])
        arsenal_ = getattr(defender_module, scenario['defender']['arsenal']['type'])
        arsenal = arsenal_(scenario['defender']['arsenal'])

        self.defender = defender_(ansible_runner, self.openstack_conn, elasticsearch_conn, config['external_ip'], config['elasticsearch']['port'], config['elasticsearch']['api_key'], arsenal)
        #self.defender = Defender(ansible_runner, self.openstack_conn, elasticsearch_conn, config['external_ip'], config['elasticsearch']['port'], config['elasticsearch']['api_key'])
        self.defender.start()
        self.goalkeeper.stop_setup_timer()

    # Start attacker
    def start_attacker(self):
        self.attacker.start_operation()
        self.goalkeeper.operation_id = self.attacker.operation_id
        print("Operation ID: " + self.attacker.operation_id)

    def finished(self):
        return not self.attacker.still_running()

    def start_main_loop(self):
        print('Main loop starting!')
        finished = False
        finish_counter = 0
        try:
            while not finished:
                self.defender.run()

                if finish_counter > 5:
                    finish_counter = 0
                    # Check if attacker has finished
                    finished = self.finished()

                time.sleep(.5)
                finish_counter += 1
        
        except KeyboardInterrupt:
            pass

    def run(self):
        time.sleep(5)
        self.goalkeeper.start_execution_timer()

        self.start_attacker()
        # Runs loop until emulation finishes
        self.start_main_loop()
        self.goalkeeper.stop_execution_timer()
        # Once finished calculate have goalkeeper measure final success metrics
        self.goalkeeper.calculate_metrics()
        self.goalkeeper.set_metric('deployment_instance', self.scenario['deployment_instance'])
        self.goalkeeper.set_metric('attacker', self.scenario['attacker'])
        self.goalkeeper.set_metric('defender', self.scenario['defender']['type'])

        
        self.goalkeeper.save_metrics()
        
        # Cleanup
        self.attacker.cleanup()
        return self.goalkeeper.metrics

    # Call if using an external stepper for the defender
    # Example: You want OpenAI gym to control the defender for learning a new policy
    def external_defender_steps(self, actions):
        return self.defender.run(actions)    


class EmulatorInteractive():
    def __init__(self, emulator):
        self.emulator = emulator
        self.commands_desc = {
            "exit": "exit emulator",
            "help": "print this help message",
            "run": "run attacker. \n\t-n <NUM> to run NUM times",
        }
        self.commands = {
            "exit":     self.handle_exit,
            "help":     self.handle_help,
            "run":      self.handle_run,
        }
    
    def print_help(self, args=[]):
        if len(args) > 0:
            print("Extra arguments found. Ignoring...")
        print("Commands:")
        for command in self.commands_desc:
            rprint(f"{command}: {self.commands_desc[command]}")
    
    def handle_exit(self, args=[]):
        if len(args) > 0:
            print("Extra arguments found. Ignoring...")
        print("Exiting emulator...")
        exit()

    def handle_run(self, args=[]):
        if len(args) > 1:
            print("Extra arguments found. Ignoring...")
        num = 1
        if "-n" in args:
            if args.index("-n") + 1 >= len(args):
                print("No number of runs specified. Ignoring...")
            else:
                num = int(args[args.index("-n") + 1])
                rprint(f"Running attacker {num} times...")

        all_metrics = []
        complete_count = 0
        error_count = 0

        for i in range(num):
            rprint(f"Starting attacker... {i+1}/{num}")
            load = self.emulator.setup(self.emulator.config, self.emulator.scenario, use_snapshots=True)
            
            if load == 1: # Failed to load snapshots. Skip this run
                error_count += 1
                all_metrics.append((i, None))
                continue
            
            metrics = self.emulator.run()
            print("Attacker finished!")
            self.emulator.goalkeeper.print_metrics()
            print("Cleaning up attacker...")
            self.emulator.attacker.cleanup()

            all_metrics.append((i, metrics))
            complete_count += 1
        
        # Print metrics for multiple runs
        # if num > 1:
        # print(f"Ran attacker {num} times\nTimes to completion: {complete_count}\nTimes fatal exit: {error_count}")
        print(f"Ran attacker {num} times\nTimes {Fore.GREEN}to completion: {Style.RESET_ALL}{complete_count}\nTimes {Fore.RED}fatal exit:{Style.RESET_ALL} {error_count}")
        for j in range(num):
            metrics = all_metrics[j][1]
            if metrics is None:
                # print(f"Run {j+1}: Failed to load snapshots")
                print(f"Run {j+1}: {Fore.RED}Failed to load snapshots{Style.RESET_ALL}")
            else:
                # print(f"Run {j+1}: Ran to completion")
                print(f"Run {j+1}: {Fore.GREEN}Ran to completion{Style.RESET_ALL}")
                rprint(metrics)


    # def handle_save(self, args=[]):
    #     metrics_file = None
    #     if len(args) > 0:
    #         metrics_file = args[0]

    #     print(f"Saving metrics to {metrics_file}...")
    #     self.emulator.goalkeeper.save_metrics(metrics_file)
    #     print("Metrics saved!")
    
    def handle_help(self, args):
        if len(args) > 0:
            print("Extra arguments found. Ignoring...")
        self.print_help()

    def start_interactive_emulator(self):
        print("Starting interactive emulator...")
        print("Type 'help' for a list of commands")
        while True:
            user_input = input("emulator> ")

            emulator_argv = user_input.split(" ")
            command = emulator_argv[0]

            if command in self.commands:
                self.commands[command](emulator_argv[1:])
            
            else:
                print("Command not recognized")
                self.print_help()
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Name of configuration file', required=True)
    parser.add_argument('-s', '--scenario', help='Name of scenario file', required=True)
    parser.add_argument('-i', '--interactive', help='Run emulator in interactive mode', action='store_true', default=False)

    parser.add_argument('-f', '--new-flags', help='INACTIVE. Create new flags for deployment. (saves new snapshots)', action='store_true', default=False)
    parser.add_argument('-d', '--debug', help='(ALWAYS ON). debug mode', action='store_true', default=False)
    
    parser.add_argument('-S', '--use-snapshots', help='Use images for setup instead', action='store_true', default=False)
    parser.add_argument('-N', '--no-deploy-network', help='Do not redeploy network topology', action='store_true', default=False)
    
    parser.add_argument('-t', '--test', help='placeholder', action='store_true', default=False)
    args = parser.parse_args()

    print(f"Starting emulator in {'' if args.interactive else 'non-'}interactive mode...")

    if args.test:
        console.log("Test mode")
        for i in track(range(10), "test"):
            console.log("test")
            time.sleep(.1)
        exit()

    # open yml config file
    with open(path.join('config', args.config), 'r') as f:
        config = yaml.safe_load(f)

    # open yml config file
    with open(path.join('scenarios', args.scenario), 'r') as f:
        scenario = yaml.safe_load(f)


    emulator = Emulator()
    
    if args.new_flags:
        rprint("This flag is currently inactive. Ignoring...")
    if args.debug:
        rprint("This flag is currently inactive. Debug mode always on. Ignoring...")

    emulator.setup(config, scenario, use_snapshots=args.use_snapshots, redeploy_network=(not args.no_deploy_network))
    emulator.run()

    # Print metrics
    emulator.goalkeeper.print_metrics()
    emulator.attacker.cleanup()

    if args.interactive:
        EmulatorInteractive(emulator).start_interactive_emulator()