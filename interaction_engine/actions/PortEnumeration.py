from .Action import Action
from ansibleRunner import run_bash_command

class PortEnumeration(Action):
    def __init__(self):
        self.foothold = None
        self.target_host = None

    def set_host_to_scan(self, foothold, target_host):
        self.foothold = foothold
        self.target_host = target_host

    def run(self, env):
        if (self.target_host is not None) and (self.foothold is not None):
            return []
        elif self.foothold is None:
            raise Exception('Please specify foothold')
        else
            raise Exception('Please specify target')

class NmapPortEnumeration(PortEnumeration):
    def run(self, env):
        pass