import os
from collections import defaultdict


class OrcehstratorTask:
    def __init__(self, name, params, host) -> None:
        self.name = name
        self.params = params
        self.host = host

    def print_tasks(self):
        print("Name: ", self.name)
        print("Params: ", self.params)
        print("Host: ", self.host)


class Orchestrator:
    def __init__(self, ansible_runner, directory) -> None:
        self.dir = directory
        self.ansible_runner = ansible_runner
        self.deployed_tasks: defaultdict[any, list[OrcehstratorTask]] = defaultdict(
            list
        )

    def print_items(self):
        print(type(self).__name__)
        for host, tasks in self.deployed_tasks.items():
            print("Host: ", host)
            for task in tasks:
                task.print_tasks()

    def add_task(self, task: OrcehstratorTask):
        self.deployed_tasks[task.host].append(task)
        self.deploy(task.name, task.params)

    def deploy(self, filename, params):
        filepath = self.dir + filename + ".yml"

        self.ansible_runner.run_playbook(filepath, playbook_params=params)
