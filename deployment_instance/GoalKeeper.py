import time
import json
import os

class GoalKeeper:

    def __init__(self, attacker):
        self.attacker = attacker
        self.flags = {}
        self.root_flags = {}
    
    def start_setup_timer(self):
        self.setup_start_time = time.time()

    def stop_setup_timer(self):
        self.metrics['setup_time'] = time.time() - self.setup_start_time
    
    def start_execution_timer(self):
        self.execution_start_time = time.time()
    
    def stop_execution_timer(self):
        self.metrics['execution_time'] = time.time() - self.execution_start_time
    
    def set_flags(self, flags):
        self.flags = flags
    
    def set_root_flags(self, root_flags):
        self.root_flags = root_flags
    
    def check_flag(self, flag):
        for host, flag_value in self.flags.items():
            if flag_value == flag:
                return host
        return None
    
    def check_root_flag(self, flag):
        for host, flag_value in self.root_flags.items():
            if flag_value == flag:
                return host
        return None

    def calculate_metrics(self):
        # TODO: Make this an object
        self.metrics = {}

        # Calculate time elapsed
        execution_time = self.execution_stop_time - self.execution_start_time
        setup_time = self.setup_stop_time - self.setup_start_time
        experiment_time = setup_time + execution_time
        
        self.metrics['experiment_time'] = experiment_time
        self.metrics['execution_time'] = execution_time
        self.metrics['setup_time'] = setup_time

        # Record flags captured
        flags_captured = []
        root_flags_captured = []
        relationships = self.attacker.get_relationships()
        for relationship in relationships:
            if relationship['source']['value'] == 'flag.txt' and relationship['edge'] == 'has_contents':
                host_flag_captured = self.check_flag(relationship['target']['value'])
                host_root_flag_captured = self.check_root_flag(relationship['target']['value'])
                if host_flag_captured is not None:
                    flags_captured.append(host_flag_captured)
                if host_root_flag_captured is not None:
                    root_flags_captured.append(host_root_flag_captured)

        self.metrics['flags_captured'] = flags_captured
        self.metrics['root_flags_captured'] = root_flags_captured

        # Record hosts infected
        hosts_infected = []
        operation_report = self.attacker.get_operation_details()
        for action in operation_report['chain']:
            if action['host'] not in hosts_infected:
                hosts_infected.append(action['host'])
        self.metrics['hosts_infected'] = hosts_infected

        return self.metrics
    
    def save_metrics(self, file_name):
        with open(os.path.join('results', file_name), 'w') as f:
            json.dump(self.metrics, f)
