from datetime import datetime
import time
import json
import os
from rich import print as rprint


class GoalKeeper:
    def __init__(self, attacker):
        self.attacker = attacker
        self.flags = {}
        self.root_flags = {}
        self.operation_id = None
        self.metrics = {}
        self.operation_log = None

    def start_setup_timer(self):
        self.setup_start_time = time.time()

    def stop_setup_timer(self):
        self.setup_stop_time = time.time()

    def set_warning(self, warning: str):
        self.metrics["warning"] = warning

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

    def set_metric(self, metric_name, metric_value):
        self.metrics[metric_name] = metric_value

    def calculate_metrics(self):
        # TODO: Make this an object
        self.metrics = {}
        self.operation_log = self.attacker.get_operation_details()

        # Calculate time elapsed
        execution_time = self.execution_stop_time - self.execution_start_time
        setup_time = self.setup_stop_time - self.setup_start_time
        experiment_time = setup_time + execution_time

        self.metrics["operation_id"] = self.operation_id
        self.metrics["start_time"] = self.setup_start_time

        self.metrics["experiment_time"] = experiment_time
        self.metrics["execution_time"] = execution_time
        self.metrics["setup_time"] = setup_time

        rprint("Flags")
        rprint(self.flags)
        rprint("Root Flags")
        rprint(self.root_flags)

        # Record flags captured
        flags_captured = []
        root_flags_captured = []
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
                flag_data = {
                    "flag": relationship["target"]["value"],
                    "host": None,
                    "type": None,
                    "created_on": flag_created_on,
                }
                if host_flag_captured is not None:
                    flag_data["host"] = host_flag_captured
                    flag_data["type"] = "user"
                    flags_captured.append(flag_data)
                if host_root_flag_captured is not None:
                    flag_data["host"] = host_root_flag_captured
                    flag_data["type"] = "root"
                    flags_captured.append(flag_data)

        self.metrics["flags_captured"] = flags_captured

        # Record hosts infected
        hosts_infected = []
        operation_report = self.attacker.get_operation_details()
        for action in operation_report["chain"]:
            if action["host"] not in hosts_infected:
                hosts_infected.append(action["host"])
        self.metrics["hosts_infected"] = hosts_infected

        return self.metrics

    def save_metrics(self, file_name=None, subdir=None):
        metrics_file = file_name
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")

        if file_name is None:
            metrics_file = "metrics-" + now_str + ".json"

        operation_log_file_name = "operation_log-" + now_str + ".json"

        if subdir is not None:
            dir_path = os.path.join("output", "metrics", subdir)
        else:
            dir_path = os.path.join("output", "metrics")

        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError as e:
                print(f"Error creating directory {dir_path}: {e}")
                return

        metrics_file = os.path.join(dir_path, metrics_file)
        operation_log_file = os.path.join(dir_path, operation_log_file_name)

        rprint(f"Saving metrics to {metrics_file}...")
        with open(metrics_file, "w") as f:
            json.dump(self.metrics, f)
        with open(operation_log_file, "w") as f:
            json.dump(self.operation_log, f)

        print("Metrics saved.")

    def print_metrics(self):
        print("Metrics:")
        rprint(self.metrics)
