from .Action import Action
from ansibleRunner import run_bash_command
import argparse
import openstackAPI
from rich import print

class PortEnumeration(Action):

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
        # TODO: 1. connect to foothold host
        conn = openstackAPI.initialize()
        manage_server, manage_ip = openstackAPI.find_manage_server(conn)
        # TODO: 2. execute "nmap host_ip" on foothold
        ansible_data_dir = '../ansible/cage/'
        ansible_vars_default = {'manage_ip': manage_ip, 'ssh_key_path': args.ssh_key_path}
        output = run_bash_command(ansible_vars_default, ansible_data_dir, 'nmap {}'.format(self.target_host))
        # TODO: 3. return output
        print(output)
        return output