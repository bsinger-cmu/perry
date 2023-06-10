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

        # Setup attacker
        caldera_api_key = config['caldera']['api_key']
        attacker_ = getattr(attacker_module, scenario['attacker'])
        self.attacker = attacker_(caldera_api_key)

        # Setup GoalKeeper
        self.goalkeeper = GoalKeeper(self.attacker)
        self.goalkeeper.start_setup_timer()

        # Deploy deployment instance
        deployment_instance_ = getattr(deployment_instance_module, scenario['deployment_instance'])
        self.deployment_instance = deployment_instance_(ansible_runner, self.openstack_conn, config['external_ip'])
        self.deployment_instance.setup(already_deployed=True)

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
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Name of configuration file')
    parser.add_argument('-s', '--scenario', help='Name of scenario file')
    args = parser.parse_args()

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
