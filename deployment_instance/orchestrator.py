import os
from collections import defaultdict

class OrchestrationTask:
    def __init__(self, name, host) -> None:
        self.name = name
        self.host = host
        self.params = {'host': host}

    def set_params(self, params):
        self.params = {**self.params, **params}

    def print_self(self):
        print("Host: ", self.host)
        print("  -  %s\t%s\n" % (self.name, str(self.params)))
    
    def print_tasks(self):
        print("  -  %s\t%s\n" % (self.name, str(self.params)))
        

class Orchestrator:
    def __init__(self, ansible_runner, directory) -> None:
        self.dir = directory
        self.ansible_runner = ansible_runner
        self.deployed_tasks: defaultdict[any, list[OrchestrationTask]] = defaultdict(list)

    def print_vulnerabilities(self):
        for host, tasks in self.deployed_tasks.items():
            print("Host: ", host)
            for task in tasks:
                task.print_tasks()

    def add_task(self, task: OrchestrationTask):
        self.deployed_tasks[task.host].append(task)
        self.deploy(task.name, task.params)

    def deploy(self, filename, params):
        filepath = self.dir + filename + ".yml"
        if not os.path.isfile(filepath):
            print("Error: File does not exist: ", filepath)
            print("Suggestion: Ensure that the file name is spelled correctly with the correct extension (.yml)")
            return
        
        self.ansible_runner.run_playbook(filepath, playbook_params=params)