from colorama import Fore, Style
from elasticsearch import Elasticsearch
from os import path
from datetime import datetime

from rich import print as rprint
import os
import uuid

from config.Config import Config
from ansible.AnsibleRunner import AnsibleRunner
from deployment_instance import GoalKeeper
from defender.arsenal import CountArsenal
from defender import Defender
from utility.logging.logging import PerryLogger, log_event, get_logger

import openstack

import time

logger = get_logger()


# Dynamically import modules
import importlib

from defender.orchestrator import OpenstackOrchestrator

deployment_instance_module = importlib.import_module("deployment_instance")
attacker_module = importlib.import_module("attacker")
defender_module = importlib.import_module("defender")
strategy_module = importlib.import_module("defender.strategy")
telemetry_module = importlib.import_module("defender.telemetry")


class Emulator:
    def __init__(self, config: Config | None = None):
        self.openstack_conn = openstack.connect(cloud="default")
        self.config: Config | None = None
        self.quiet = False
        self.scenario = None

    def set_quiet(self, quiet):
        self.quiet = quiet

    def set_config(self, config: Config):
        self.config = config

    def set_scenario(self, scenario):
        self.scenario = scenario

    def setup(
        self,
        output_dir=None,
        compile=False,
        network_setup=True,
        host_setup=True,
        experiment_id=None,
    ):
        if output_dir is None:
            output_dir = "./output/misc"

        if self.scenario is None:
            raise Exception("Scenario not set")

        if self.config is None:
            raise Exception("Config not set")

        if experiment_id is None:
            experiment_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        experiment_dir = path.join(output_dir, experiment_id)
        rprint(f"Experiment directory: {experiment_dir}")

        # Create experiment directory
        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)

        # Setup defender logging
        PerryLogger.setup_logger(experiment_dir)

        # Setup connection to elasticsearch
        elasticsearch_server = f"https://localhost:{self.config.elastic_config.port}"
        elasticsearch_api_key = self.config.elastic_config.api_key

        elasticsearch_conn = Elasticsearch(
            elasticsearch_server,
            basic_auth=("elastic", elasticsearch_api_key),
            verify_certs=False,
        )
        # check if connection is successful
        if not elasticsearch_conn.ping():
            raise Exception("Connection to elasticsearch failed")

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
        ssh_key_path = self.config.openstack_config.ssh_key_path
        ansible_dir = "./ansible/"
        ansible_runner = AnsibleRunner(
            ssh_key_path, None, ansible_dir, experiment_dir, self.quiet
        )

        # Setup attacker module
        caldera_api_key = self.config.caldera_config.api_key
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
            ansible_runner, self.openstack_conn, self.config.external_ip, self.config
        )

        # Compile deployment instance if needed
        if compile:
            self.deployment_instance.compile(
                setup_network=network_setup, setup_hosts=host_setup
            )
            return
        else:
            # Restore all hosts in environment
            # Do it before Caldera is on so old agents are removed
            self.deployment_instance.setup()

        # Start caldera server after deployment instance is setup
        if not self.config.caldera_config.external:
            self.attacker.start_server(
                self.config.caldera_config.python_path,
                self.config.caldera_config.caldera_path,
            )

        # Do runtime setup like starting initial attacker agent
        self.deployment_instance.runtime_setup()

        self.goalkeeper.set_flags(self.deployment_instance.flags)
        self.goalkeeper.set_root_flags(self.deployment_instance.root_flags)

        # Setup initial defender
        ### Telemetry ###
        telemetry_ = getattr(telemetry_module, self.scenario.defender.telemetry)
        telemetry = telemetry_(elasticsearch_conn, self.deployment_instance.network)

        ### Arsenal ###
        arsenal = CountArsenal(self.scenario.defender.capabilities)

        ### Orchestration ###
        external_ip = self.config.external_ip
        elastic_search_port = self.config.elastic_config.port
        external_elasticsearch_server = f"https://{external_ip}:{elastic_search_port}"
        orchestrator = OpenstackOrchestrator(
            self.openstack_conn,
            ansible_runner,
            external_elasticsearch_server,
            self.config.elastic_config.api_key,
            self.config,
            self.deployment_instance.network,
        )

        ### Strategy ###
        strategy_ = getattr(strategy_module, self.scenario.defender.strategy)
        strategy = strategy_(arsenal, self.deployment_instance.network, orchestrator)

        self.defender = Defender(
            arsenal, strategy, telemetry, orchestrator, self.deployment_instance.network
        )

        self.defender.start()
        self.goalkeeper.stop_setup_timer()

    # Start attacker
    def start_attacker(self):
        # Delete old agents from prior experiments
        self.attacker.delete_agents()
        self.attacker.start_operation()
        self.goalkeeper.operation_id = self.attacker.operation_id
        logger.debug("Operation ID: " + self.attacker.operation_id)

    def finished(self):
        return not self.attacker.still_running()

    def start_main_loop(self, timeout_minutes):
        log_event("Emulator", "Main loop starting!")

        # Create timer
        start_time = time.time()
        timeout = timeout_minutes * 60

        finished = False
        finish_counter = 0
        instance_check_counter = 0

        while not finished:
            current_time = time.time()
            elapsed_time = current_time - start_time  # Calculate the elapsed time
            if (
                elapsed_time > timeout
            ):  # Check if the elapsed time is greater than the timeout
                logger.info(f"Timeout reached!")
                break

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

        self.attacker.stop_operation()

    def run(self, timeout: int):
        """
        start running the emulator.
        This does the setup and then runs the attacker and main loop
        """
        log_event("Emulator", "Starting emulation!")
        if self.scenario is None:
            raise Exception("Scenario not set")

        time.sleep(5)
        self.goalkeeper.start_execution_timer()

        self.start_attacker()
        # Runs loop until emulation finishes
        self.start_main_loop(timeout)
        self.goalkeeper.stop_execution_timer()
        # Once finished calculate have goalkeeper measure final success metrics
        result = self.goalkeeper.calculate_metrics(self.scenario, self.defender)

        log_event("Emulator", "Attacker finished")
        self.goalkeeper.print_metrics()
        # Cleanup

        # Save attacker logs
        output_dir = self.goalkeeper.output_dir
        self.attacker.save_logs(output_dir)

        log_event("Emulator", "Cleaning up attacker...")
        self.attacker.cleanup()

        log_event("Emulator", "Saving metrics...")
        self.goalkeeper.save_metrics()

        log_event("Emulator", "Emulation finished!")
        return result

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
