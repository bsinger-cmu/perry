from .Action import Action
from ansibleRunner import run_bash_command

class PortEnumeration(Action):
    def __init__(self):
        self.foothold = None
        self.target_host = None

    # TODO: set default management host ip_address
    def set_host_to_scan(self, target_host, foothold="management_host"):
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
        # TODO: 
        # 1. check attacker's access to the foothold host
        # 2. connect to foothold host
        # 3. execute "nmap host_ip" on foothold
        # 4. return output
        pass