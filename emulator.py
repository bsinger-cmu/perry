import argparse
from typing import NoReturn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

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

from colorama import Fore, Back, Style

class Emulator:

    def __init__(self):
        # Initialize connection
        self.openstack_conn = openstack.connect(cloud='default')

        self.scenario = None
        self.config = None
        self.output_subdir = None

    def set_output_subdir(self, subdir):
        self.output_subdir = subdir

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

        # Delete all decoy instances on openstack
        all_servers = self.openstack_conn.list_servers()
        deleted_decoys = False
        for server in all_servers:
            if 'decoy' in server.name:
                print(f"Deleting decoy server: {server.name}")
                self.openstack_conn.delete_server(server.id)
                deleted_decoys = True
        if deleted_decoys:
            time.sleep(5)

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

        self.goalkeeper.metrics = self.goalkeeper.metrics | self.defender.metrics
        
        print("Attacker finished!")
        self.goalkeeper.print_metrics()
        # Cleanup
        
        print("Cleaning up attacker...")
        self.attacker.cleanup()

        print("Saving metrics...")
        self.goalkeeper.save_metrics(subdir=self.output_subdir)
        return self.goalkeeper.metrics

    # Call if using an external stepper for the defender
    # Example: You want OpenAI gym to control the defender for learning a new policy
    def external_defender_steps(self, actions):
        return self.defender.run(actions)



class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError("ERROR", message)

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        if status == 0:
            return
        print("EXIT", status, message)

class EmulatorInteractive():
    def __init__(self, emulator, config=None, scenario=None):
        self.emulator = emulator
        self.config = config
        self.scenario = scenario

        self.session = PromptSession(history=FileHistory('.emulator_history'))

        self.emulator_parser = ArgumentParser(prog="emulator", add_help=False, exit_on_error=False,)
        subparsers = self.emulator_parser.add_subparsers()

        run_parser = subparsers.add_parser('run', help='run the attacker')
        run_parser.add_argument('-n', '--num', help='number of times to run attacker', type=int, default=1)
        run_parser.set_defaults(func=self.handle_run)

        help_parser = subparsers.add_parser('help', help='print help message')
        help_parser.set_defaults(func=self.handle_help)

        exit_parser = subparsers.add_parser('exit', help='exit emulator')
        exit_parser.set_defaults(func=self.handle_exit)

        setup_parser = subparsers.add_parser('setup', help='setup scenario')
        setup_parser.add_argument('-c', '--config', help='Name of configuration file', required=True)
        setup_parser.add_argument('-s', '--scenario', help='Name of scenario file', required=True)
        setup_parser.add_argument('-S', '--use-snapshots', help='Use images for setup instead', action='store_true', default=False)
        setup_parser.add_argument('-R', '--redeploy-network', help='Redeploy network topology', action='store_true', default=False)
        setup_parser.add_argument('-o', '--output', help='Output subdir for metrics', default=None)
        setup_parser.set_defaults(func=self.handle_setup)


        # load_parser = subparsers.add_parser('load', help='load experiment instructions from file')


    def handle_setup(self, args):
        with open(path.join('config', config), 'r') as f:
            config = yaml.safe_load(f)

        # open yml config file
        with open(path.join('scenarios', scenario), 'r') as f:
            scenario = yaml.safe_load(f)

        self.emulator.set_output_subdir(args.output)
        self.emulator.setup(args.config, args.scenario, use_snapshots=args.use_snapshots, redeploy_network=args.redeploy_network)
        return

    def handle_run(self, args):
        if self.emulator.config is None or self.emulator.scenario is None:
            print("No config or scenario loaded. Run setup first")
            return

        num = args.num
        rprint(f"Running attacker {num} times...")
        all_metrics = []
        all_statuses = []

        complete_count = 0
        error_count = 0
        exception_count = 0
        emulator_task = progress.add_task("[green]Running Experiment", start=False, total=num)

        with progress:
            progress.start_task(emulator_task)
            for i in range(num):
                rprint(f"Starting attacker... {i+1}/{num}")
                
                try:
                    load = self.emulator.setup(self.emulator.config, self.emulator.scenario, use_snapshots=True)
                except Exception as e:
                    print(f"{Back.RED}Failed with exception:{Style.RESET_ALL}")
                    print(e)
                    error_count += 1
                    exception_count += 1
                    all_metrics.append((i, "Exception", e))
                    progress.advance(emulator_task)
                    continue

                if load == 1: # Failed to load snapshots. Skip this run
                    error_count += 1
                    print(f"{Fore.RED}Failed to load snapshots{Style.RESET_ALL}")
                    all_metrics.append((i, "Error", "Failed to load snapshots"))
                    progress.advance(emulator_task)
                    continue
                
                try:
                    metrics = self.emulator.run()
                except:
                    print(f"{Back.RED}Failed with exception:{Style.RESET_ALL}")
                    print(e)
                    exception_count += 1
                    all_metrics.append((i, "Exception", e))
                    progress.advance(emulator_task)
                    continue

                all_metrics.append((i, metrics))
                complete_count += 1
                progress.advance(emulator_task)

        progress.remove_task(emulator_task)
        
        # Print metrics for multiple runs
        for j in range(num):
            metrics = all_metrics[j][1]
            if metrics == "Error":
                print(f"Run {j+1}: {Fore.RED}Failed to load snapshots{Style.RESET_ALL}")
            elif metrics == "Exception":
                print(f"Run {j+1}: {Back.RED}Failed with exception:{Style.RESET_ALL}\n{all_metrics[j][2]}")
            else:
                print(f"Run {j+1}: {Fore.GREEN}Ran to completion{Style.RESET_ALL}")
                rprint(metrics)

        print(f"Total number of experiments runs:     {num}")
        print(f"Times {Fore.GREEN}to completion:                  {Style.RESET_ALL}{complete_count}")
        print(f"Times {Fore.RED}failed to load snapshots:       {Style.RESET_ALL}{error_count}")
        print(f"Times {Back.RED}failed with exception:          {Style.RESET_ALL}{exception_count}")
    
    def handle_exit(self, _):
        print("Exiting emulator...")
        exit()

    def handle_help(self, _):
        self.emulator_parser.print_help()

    def start_interactive_emulator(self):
        print("Starting interactive emulator...")
        print("Type 'help' for a list of commands")
        while True:
            user_input = self.session.prompt("emulator> ", auto_suggest=AutoSuggestFromHistory())

            emulator_argv = user_input.split(" ")

            try:
                args = self.emulator_parser.parse_args(emulator_argv)
                if not ('--help' in emulator_argv or '-h' in emulator_argv) and hasattr(args, 'func'):
                    args.func(args)
                    print()
                    
            except argparse.ArgumentError as e:
                print(e)
                self.emulator_parser.print_help()
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Name of configuration file', required=False)
    parser.add_argument('-s', '--scenario', help='Name of scenario file', required=False)

    parser.add_argument('-i', '--interactive', help='Run emulator in interactive mode', action='store_true', default=False)

    parser.add_argument('-o', '--output', help='Output subdir in metrics dir', default=None)

    parser.add_argument('-S', '--use-snapshots', help='Use images for setup instead', action='store_true', default=False)
    parser.add_argument('-R', '--redeploy-network', help='Redeploy network topology', action='store_true', default=False)
    
    parser.add_argument('-t', '--test', help='placeholder', action='store_true', default=False)

    parser.add_argument('-d', '--debug', help='(ALWAYS ON). debug mode', action='store_true', default=False)
    args = parser.parse_args()

    print(f"Starting emulator in {'' if args.interactive else 'non-'}interactive mode...")
    
    if args.debug:
        rprint("This flag is currently inactive. Debug mode always on. Ignoring...")

    # open yml config file
    if args.config:
        with open(path.join('config', args.config), 'r') as f:
            config = yaml.safe_load(f)

    # open yml config file
    if args.scenario:
        with open(path.join('scenarios', args.scenario), 'r') as f:
            scenario = yaml.safe_load(f)

    emulator = Emulator()

    if args.output:
        emulator.set_output_subdir(args.output)

    if args.interactive:
        if (not args.use_snapshots):
            emulator.setup(config, scenario, use_snapshots=args.use_snapshots, redeploy_network=args.redeploy_network)
        
        emulator.scenario = scenario
        emulator.config = config
        EmulatorInteractive(emulator).start_interactive_emulator()

    else:
        emulator.setup(config, scenario, use_snapshots=args.use_snapshots, redeploy_network=args.redeploy_network)
        emulator.run()

        # Print metrics
        emulator.goalkeeper.print_metrics()
        emulator.attacker.cleanup()