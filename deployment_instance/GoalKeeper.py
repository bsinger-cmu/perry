import time
import json
import os

class GoalKeeper:

    def __init__(self, attacker):
        self.attacker = attacker
        self.flags = {}
    
    def start_setup_timer(self):
        self.setup_start_time = time.time()
    
    def start_execution_timer(self):
        self.execution_start_time = time.time()
    
    def set_flags(self, flags):
        self.flags = flags
    
    def check_flag(self, flag):
        for host, flag_value in self.flags.items():
            if flag_value == flag:
                return host
        
        return None

    def calculate_metrics(self):
        # TODO: Make this an object
        self.metrics = {}

        # Calculate time elapsed
        experiment_time = time.time() - self.setup_start_time
        execution_time = time.time() - experiment_time
        setup_time = self.execution_start_time - self.setup_start_time
        
        self.metrics['experiment_time'] = experiment_time
        self.metrics['execution_time'] = execution_time
        self.metrics['setup_time'] = setup_time

        # Record flags captured
        flags_captured = []
        relationships = self.attacker.get_relationships()
        for relationship in relationships:
            if relationship['source']['value'] == 'flag.txt' and relationship['edge'] == 'has_contents':
                host_flag_captured = self.check_flag(relationship['target']['value'])
                if host_flag_captured is not None:
                    flags_captured.append(host_flag_captured)
        self.metrics['flags_captured'] = flags_captured

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
