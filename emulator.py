from colorama import Fore, Style
from elasticsearch import Elasticsearch
from os import path

from rich import print as rprint
import os
import uuid

from ansible.AnsibleRunner import AnsibleRunner
from deployment_instance import GoalKeeper
from scenarios.Scenario import Scenario
from defender.arsenal import CountArsenal
from defender import Defender
from utility.logging.logging import setup_logger_for_emulation, log_event

import openstack

import time


# Dynamically import modules
import importlib

from defender.orchestrator import OpenstackOrchestrator

deployment_instance_module = importlib.import_module("deployment_instance")
attacker_module = importlib.import_module("attacker")
defender_module = importlib.import_module("defender")
strategy_module = importlib.import_module("defender.strategy")
telemetry_module = importlib.import_module("defender.telemetry")


class Emulator:
    scenario: Scenario

    def __init__(self):
        self.openstack_conn = openstack.connect(cloud="default")
        self.config = None
        self.quiet = False

    def set_quiet(self, quiet):
        self.quiet = quiet

    def set_config(self, config):
        self.config = config

    def set_scenario(self, scenario):
        self.scenario = scenario

    def setup(
        self, output_dir=None, compile=False, network_setup=True, host_setup=True
    ):
        if output_dir is None:
            output_dir = "./output/misc"

        experiment_id = str(uuid.uuid4())
        experiment_dir = path.join(output_dir, experiment_id)

        # Create experiment directory
        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)

        # Setup defender logging
        setup_logger_for_emulation(experiment_dir)

        # Setup connection to elasticsearch
        elasticsearch_server = (
            f"https://localhost:{self.config['elasticsearch']['port']}"
        )
        elasticsearch_api_key = self.config["elasticsearch"]["api_key"]

        elasticsearch_conn = Elasticsearch(
            elasticsearch_server,
            basic_auth=("elastic", elasticsearch_api_key),
            verify_certs=False,
        )

        log_event("Emulator setup", "Setting up elastic search connection")
        log_event("Emulator setup", f"Elastic search server: {elasticsearch_server}")
        log_event("Emulator setup", f"Elastic search api key: {elasticsearch_api_key}")

        # Delete all decoy instances on openstack
        all_servers = self.openstack_conn.list_servers()
        deleted_decoys = False
        for server in all_servers:
            if "decoy" in server.name:
                print(f"Deleting decoy server: {server.name}")
                self.openstack_conn.delete_server(server.id)
                deleted_decoys = True
        if deleted_decoys:
            time.sleep(5)

        # Initialize ansible
        ssh_key_path = self.config["ssh_key_path"]
        ansible_dir = "./ansible/"
        ansible_runner = AnsibleRunner(
            ssh_key_path, None, ansible_dir, experiment_dir, self.quiet
        )

        # Setup attacker
        caldera_api_key = self.config["caldera"]["api_key"]
        self.caldera_api_key = caldera_api_key
        attacker_ = getattr(attacker_module, self.scenario.attacker.name)
        self.attacker = attacker_(caldera_api_key, experiment_id)

        # Setup GoalKeeper
        self.goalkeeper = GoalKeeper(self.attacker, experiment_dir)
        self.goalkeeper.start_setup_timer()

        # Deploy deployment instance
        deployment_instance_ = getattr(
            deployment_instance_module, self.scenario.deployment_instance.name
        )
        self.deployment_instance = deployment_instance_(
            ansible_runner, self.openstack_conn, self.config["external_ip"]
        )

        # Compile deployment instance if needed
        if compile:
            self.deployment_instance.compile(
                setup_network=network_setup, setup_hosts=host_setup
            )
        else:
            # Do runtimesetup
            self.deployment_instance.run()

        self.deployment_instance.print_all_flags()

        self.goalkeeper.set_flags(self.deployment_instance.flags)
        self.goalkeeper.set_root_flags(self.deployment_instance.root_flags)

        # Setup initial defender
        ### Telemetry ###
        telemetry_ = getattr(telemetry_module, self.scenario.defender.telemetry)
        telemetry = telemetry_(elasticsearch_conn)

        ### Arsenal ###
        arsenal = CountArsenal(self.scenario.defender.capabilities)

        ### Strategy ###
        strategy_ = getattr(strategy_module, self.scenario.defender.strategy)
        strategy = strategy_(arsenal)

        ### Orchestration ###
        external_ip = self.config["external_ip"]
        elastic_search_port = self.config["elasticsearch"]["port"]
        external_elasticsearch_server = f"https://{external_ip}:{elastic_search_port}"
        orchestrator = OpenstackOrchestrator(
            self.openstack_conn,
            ansible_runner,
            external_elasticsearch_server,
            self.config["elasticsearch"]["api_key"],
        )

        self.defender = Defender(arsenal, strategy, telemetry, orchestrator)

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
        log_event("Emulator", "Main loop starting!")
        finished = False
        finish_counter = 0
        instance_check_counter = 0
        try:
            while not finished:
                self.defender.run()

                if finish_counter > 5:
                    finish_counter = 0
                    # Check if attacker has finished
                    finished = self.finished()

                if instance_check_counter > 60:
                    instance_check_counter = 0
                    self.check_all_instances()

                time.sleep(0.5)
                finish_counter += 1

        except KeyboardInterrupt:
            pass

    def run(self):
        """
        start running the emulator.
        This does the setup and then runs the attacker and main loop
        """
        time.sleep(5)
        self.goalkeeper.start_execution_timer()

        self.start_attacker()
        # Runs loop until emulation finishes
        self.start_main_loop()
        self.goalkeeper.stop_execution_timer()
        # Once finished calculate have goalkeeper measure final success metrics
        self.goalkeeper.calculate_metrics()
        self.goalkeeper.set_metric(
            "deployment_instance", self.scenario["deployment_instance"]
        )
        self.goalkeeper.set_metric("attacker", self.scenario["attacker"])
        self.goalkeeper.set_metric("defender", self.scenario["defender"]["type"])

        self.goalkeeper.metrics = self.goalkeeper.metrics | self.defender.metrics

        log_event("Emulator", "Attacker finished")
        self.goalkeeper.print_metrics()
        # Cleanup

        log_event("Emulator", "Cleaning up attacker...")
        self.attacker.cleanup()

        log_event("Emulator", "Saving metrics...")
        self.goalkeeper.save_metrics()

        log_event("Emulator", "Emulation finished!")
        return self.goalkeeper.metrics

    # Call if using an external stepper for the defender
    # Example: You want OpenAI gym to control the defender for learning a new policy
    def external_defender_steps(self, actions):
        return self.defender.run(actions)

    def check_all_instances(self):
        all_servers = self.openstack_conn.list_servers()
        all_active = True
        for server in all_servers:
            if server.status != "ACTIVE":
                print(
                    f"{Fore.RED}Server {server.name} is in {server.status} state {Style.RESET_ALL}"
                )
                all_active = False

            if server.status == "ERROR":
                print(f"An error has occured in server {server.name}.")
                print(f"Server {server.name} is in ERROR state")
                print(f"Placing warning in goalkeeper metrics")
                self.goalkeeper.set_warning(f"server_error_state")
