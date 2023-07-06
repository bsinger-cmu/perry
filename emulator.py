import argparse

from AnsibleRunner import AnsibleRunner
from deployment_instance import SimpleInstanceV1, GoalKeeper

import openstack

import time

# Dynamically import modules
import importlib
deployment_instance_module = importlib.import_module('deployment_instance')
defender_module = importlib.import_module('defender')
attacker_module = importlib.import_module('attacker')

from attacker import Attacker, TwoPathAttacker
from defender import WaitAndSpotDefender, Defender

from rich import print
from os import path
import yaml
from elasticsearch import Elasticsearch


class Emulator:

    def __init__(self):
        # Initialize connection
        self.openstack_conn = openstack.connect(cloud='default')
        self.scenario = None
        self.config = None
        

    def setup(self, config, scenario):
        # Setup connection to elasticsearch
        elasticsearch_server = f"https://localhost:{config['elasticsearch']['port']}"
        elasticsearch_api_key = config['elasticsearch']['api_key']

        elasticsearch_conn = Elasticsearch(
            elasticsearch_server,
            basic_auth=("elastic", elasticsearch_api_key),
            verify_certs=False
        )

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
        
        self.deployment_instance.setup(already_deployed=False)

        self.goalkeeper.set_flags(self.deployment_instance.flags)
        self.goalkeeper.start_execution_timer()
        
        # Setup initial defender
        defender_ = getattr(defender_module, scenario['defender']['type'])
        arsenal_ = getattr(defender_module, scenario['defender']['arsenal']['type'])
        arsenal = arsenal_(scenario['defender']['arsenal'])

        self.defender = defender_(ansible_runner, self.openstack_conn, elasticsearch_conn, config['external_ip'], config['elasticsearch']['port'], config['elasticsearch']['api_key'], arsenal)
        #self.defender = Defender(ansible_runner, self.openstack_conn, elasticsearch_conn, config['external_ip'], config['elasticsearch']['port'], config['elasticsearch']['api_key'])
        self.defender.start()

    # Start attacker
    def start_attacker(self):
        self.attacker.start_operation()

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
        self.goalkeeper.start_execution_timer()

        self.start_attacker()
        # Runs loop until emulation finishes
        self.start_main_loop()
        # Once finished calculate have goalkeeper measure final success metrics
        metrics = self.goalkeeper.calculate_metrics()
        # Cleanup
        self.attacker.cleanup()

        return metrics

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
            "run": "run attacker",
            "save <metrics.json>": "save metrics to file (default: metrics.json)",
            "set <attacker> <value>": "set attacker to <attacker>",
            "reset <attacker>": "set attacker to <attacker>",
        }
        self.commands = {
            "exit": self.handle_exit,
            "help": self.handle_help,
            "run":  self.handle_run,
            "save": self.handle_save,
            "reset":  self.handle_reset,
            "set":  self.handle_set,
        }
    
    def print_help(self, args=[]):
        if len(args) > 0:
            print("Extra arguments found. Ignoring...")
        print("Commands:")
        for command in self.commands_desc:
            print(f"{command}: {self.commands_desc[command]}")
    
    def handle_exit(self, args=[]):
        if len(args) > 0:
            print("Extra arguments found. Ignoring...")
        print("Exiting emulator...")
        exit()

    def handle_run(self, args=[]):
        if len(args) > 0:
            print("Extra arguments found. Ignoring...")
        print("Starting attacker...")
        metrics = self.emulator.run()
        print("Attacker finished!")
        print("Metrics:")
        print(metrics)

    def handle_save(self, args):
        metrics_file = "metrics.json"
        if len(args) > 0:
            metrics_file = args[0]
        print(f"Saving metrics to {metrics_file}...")
        self.emulator.goalkeeper.save_metrics(metrics_file)
        print("Metrics saved!")
    
    def handle_help(self, args):
        if len(args) > 0:
            print("Extra arguments found. Ignoring...")
        self.print_help()

    def handle_set(self, args):
        if len(args) != 2:
            print("Improper usage. No changes made.")
            print("Usage: reset <attacker> <type>")
            return
        
        if args[0] != "attacker":
            print("Invalid argument. No changes made.")
            return

        attacker = args[1]
        attacker_ = getattr(attacker_module, attacker, None)
        if attacker_ == None:
            print("Attacker not found. No changes made.")
        else:
            self.emulator.attacker = attacker_(self.emulator.caldera_api_key)
            print(f"Attacker set to {attacker}!")

    def handle_reset(self, args):
        if len(args) != 1:
            print("Improper usage. No changes made.")
            print("Usage: reset <attacker>")
            return
        
        if args[0] != "attacker":
            print("Invalid argument. No changes made.")
            print("Usage: reset <attacker>")
            return

        attacker = self.emulator.scenario['attacker']['type']
        attacker_ = getattr(attacker_module, attacker, None)
        if attacker_ == None:
            print("Attacker not found. No changes made.")
        else:
            self.emulator.attacker = attacker_(self.emulator.caldera_api_key)
            print(f"Attacker set to {attacker}!")

    def start_interactive_emulator(self):
        print("Starting interactive emulator...")
        print("Type 'help' for a list of commands")
        while True:
            user_input = input("emulator> ")

            emulator_argv = user_input.split(" ")
            command = emulator_argv[0]

            # if command == "run":
            #     emulator.run()
            
            # elif command == "exit":
            #     break
            
            # elif command == "save":
            #     if emulator_argc == 2:
            #         metrics_file = emulator_argv[1]
            #     else:
            #         metrics_file = "metrics.json"
            #     emulator.goalkeeper.save_metrics(metrics_file)

            # elif command == "set":
            #     if emulator_argc == 3 and emulator_argv[1] == "attacker":
            #         attacker_ = getattr(attacker_module, emulator_argv[2], None)
            #         if attacker_ == None:
            #             print("Attacker not found. No changes made.")
            #         else:
            #             emulator.attacker = attacker_(emulator.caldera_api_key)
            #             print("Attacker set to %s." % emulator_argv[2])
            #     else:
            #         print("Invalid use of set command.")
            #         print("Usage: set <attacker> <value>")

            # elif command == "help":
            #     self.print_help()

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
    args = parser.parse_args()

    print(f"Starting emulator in {'' if args.interactive else 'non-'}interactive mode...")

    # open yml config file
    with open(path.join('config', args.config), 'r') as f:
        config = yaml.safe_load(f)

    # open yml config file
    with open(path.join('scenarios', args.scenario), 'r') as f:
        scenario = yaml.safe_load(f)

    emulator = Emulator()
    emulator.setup(config, scenario)
    
    emulator.run()

    # Print metrics
    print(emulator.goalkeeper.metrics)
    emulator.goalkeeper.save_metrics('metrics.json')


    if args.interactive:
        EmulatorInteractive(emulator).start_interactive_emulator()