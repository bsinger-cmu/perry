from colorama import Fore, Back, Style
from elasticsearch import Elasticsearch
import yaml
from os import path
import re
import rich.progress as rpg
from rich.progress import track
from console import console, progress
from rich import print as rprint
from defender import WaitAndSpotDefender, Defender
from attacker import Attacker, TwoPathAttacker
import argparse
import copy
import os
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

deployment_instance_module = importlib.import_module("deployment_instance")
defender_module = importlib.import_module("defender")
attacker_module = importlib.import_module("attacker")


class Emulator:
    def __init__(self):
        self.openstack_conn = openstack.connect(cloud="default")

        self.scenario = None
        self.config = None
        self.output_subdir = None
        self.quiet = False

    def set_quiet(self, quiet):
        self.quiet = quiet

    def set_config(self, config):
        self.config = config

    def set_scenario(self, scenario):
        self.scenario = scenario

    def safe_create_dir(self, dir_path):
        """
        safely create a directory
        """
        if not path.exists(dir_path):
            print(f"Creating directory {dir_path}")
            try:
                os.makedirs(dir_path)
            except OSError as e:
                print(f"Error creating directory {dir_path}: {e}")
                return

    def set_output_subdir(self, subdir):
        """
        set the output directory and ensure that the results and metrics directories exist
        If not, create them
        """
        if subdir is not None:
            self.output_subdir = subdir
            dirs_to_make = [
                os.path.join("results", subdir),
                os.path.join("metrics", subdir),
            ]

            for dir_to_make in dirs_to_make:
                self.safe_create_dir(dir_to_make)

    def setup(self, compile=False, network_only=False):
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
        ansible_runner = AnsibleRunner(ssh_key_path, None, ansible_dir, self.quiet)

        # Setup attacker
        caldera_api_key = self.config["caldera"]["api_key"]
        self.caldera_api_key = caldera_api_key
        attacker_ = getattr(attacker_module, self.scenario["attacker"])
        self.attacker = attacker_(caldera_api_key)

        # Setup GoalKeeper
        self.goalkeeper = GoalKeeper(self.attacker)
        self.goalkeeper.start_setup_timer()

        # Deploy deployment instance
        deployment_instance_ = getattr(
            deployment_instance_module, self.scenario["deployment_instance"]
        )
        self.deployment_instance = deployment_instance_(
            ansible_runner, self.openstack_conn, self.config["external_ip"]
        )

        # Compile deployment instance if needed
        if compile:
            self.deployment_instance.compile(network_only=network_only)
        else:
            # Do runtimesetup
            self.deployment_instance.run()

        self.deployment_instance.print_all_flags()

        self.goalkeeper.set_flags(self.deployment_instance.flags)
        self.goalkeeper.set_root_flags(self.deployment_instance.root_flags)

        # Setup initial defender
        defender_ = getattr(defender_module, self.scenario["defender"]["type"])
        arsenal_ = getattr(
            defender_module, self.scenario["defender"]["arsenal"]["type"]
        )
        arsenal = arsenal_(self.scenario["defender"]["arsenal"])

        self.defender = defender_(
            ansible_runner,
            self.openstack_conn,
            elasticsearch_conn,
            self.config["external_ip"],
            self.config["elasticsearch"]["port"],
            self.config["elasticsearch"]["api_key"],
            arsenal,
        )
        # self.defender = Defender(ansible_runner, self.openstack_conn, elasticsearch_conn, config['external_ip'], config['elasticsearch']['port'], config['elasticsearch']['api_key'])
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
        print("Main loop starting!")
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
