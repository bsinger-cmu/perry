from datetime import datetime
import time
import json
import os
from rich import print as rprint

from utility.logging import log_event
from .Result import ExperimentResult, FlagInformation, FlagType, DataExfiltrated
from scenarios.Scenario import Scenario
from defender import Defender


class GoalKeeper:
    def __init__(self, attacker, output_dir):
        self.attacker = attacker
        self.flags = {}
        self.root_flags = {}
        self.operation_id = ""
        self.operation_log = None
        self.output_dir = output_dir

    def start_setup_timer(self):
        self.setup_start_time = time.time()

    def stop_setup_timer(self):
        self.setup_stop_time = time.time()

    def start_execution_timer(self):
        self.execution_start_time = time.time()

    def stop_execution_timer(self):
        self.execution_stop_time = time.time()

    def set_flags(self, flags):
        self.flags = flags

    def set_root_flags(self, root_flags):
        self.root_flags = root_flags

    def check_flag(self, flag):
        for host, flag_value in self.flags.items():
            # print(f"flag_value: {flag_value} looking for flag: {flag}, host: {host}")
            if flag_value == flag:
                return host
        return None

    def check_root_flag(self, flag):
        for host, flag_value in self.root_flags.items():
            # print(f"flag_value: {flag_value} looking for flag: {flag}, host: {host}")
            if flag_value == flag:
                return host
        return None

    def calculate_metrics(self, scenario: Scenario, defender: Defender):
        # TODO: Make this an object
        self.operation_log = self.attacker.get_operation_details()

        # Calculate time elapsed
        execution_time = self.execution_stop_time - self.execution_start_time
        setup_time = self.setup_stop_time - self.setup_start_time
        experiment_time = setup_time + execution_time

        # Record flags captured
        flags_captured: list[FlagInformation] = []
        data_exfiltrated = []

        relationships = self.attacker.get_relationships()
        for relationship in relationships:
            if (
                "flag.txt" in relationship["source"]["value"]
                and relationship["edge"] == "has_contents"
            ):
                host_flag_captured = self.check_flag(relationship["target"]["value"])
                host_root_flag_captured = self.check_root_flag(
                    relationship["target"]["value"]
                )
                flag_created_on = relationship["source"]["created"]
                flag_name = relationship["target"]["value"]

                if host_flag_captured is not None:
                    flag = FlagInformation(
                        flag=flag_name,
                        host=host_flag_captured,
                        type=FlagType.USER,
                        time_found=flag_created_on,
                    )
                    flags_captured.append(flag)
                if host_root_flag_captured is not None:
                    flag = FlagInformation(
                        flag=flag_name,
                        host=host_root_flag_captured,
                        type=FlagType.ROOT,
                        time_found=flag_created_on,
                    )
                    flags_captured.append(flag)
            if "results.data" in relationship["source"]["trait"]:
                if relationship["edge"] == "has_timestamp":
                    filename = relationship["source"]["value"]
                    timestamp = relationship["target"]["value"]
                    time_exfiltrated = timestamp - self.execution_start_time
                    data_exfiltrated.append(
                        DataExfiltrated(
                            name=filename, time_exfiltrated=time_exfiltrated
                        )
                    )

        # Record hosts infected
        hosts_infected = []
        operation_report = self.attacker.get_operation_details()
        for action in operation_report["chain"]:
            if action["host"] not in hosts_infected:
                hosts_infected.append(action["host"])

        self.results = ExperimentResult(
            scenario=scenario,
            experiment_time=experiment_time,
            execution_time=execution_time,
            setup_time=setup_time,
            flags_captured=flags_captured,
            data_exfiltrated=data_exfiltrated,
            hosts_infected=hosts_infected,
            operation_id=self.operation_id,
            defender_action_counts=defender.orchestrator.action_counts,
        )

        return self.results

    def save_metrics(self):
        result_file = "result.json"
        result_file = os.path.join(self.output_dir, result_file)

        operation_log_file_name = "operation_log.json"
        operation_log_file = os.path.join(self.output_dir, operation_log_file_name)

        log_event("GoalKeeper", f"Saving results to file: {result_file}")
        log_event("GoalKeeper", f"Saving operations to file: {operation_log_file}")

        with open(result_file, "w") as f:
            result_data = self.results.model_dump()
            json.dump(result_data, f)
        with open(operation_log_file, "w") as f:
            json.dump(self.operation_log, f)

    def print_metrics(self):
        print("Metrics:")
        rprint(self.results)
