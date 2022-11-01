import ansible_runner
import argparse
from rich import print


class AnsibleRunner:
    def __init__(self, ssh_key_path, management_ip, ansible_dir, inventory):
        self.ssh_key_path = ssh_key_path
        self.management_ip = management_ip
        self.ansible_dir = ansible_dir
        self.inventory = 'inventories/' + inventory

        self.ansible_vars_default = {'manage_ip': self.management_ip, 'ssh_key_path': self.ssh_key_path}

    def run_playbook(self, playbook_name, playbook_params=None):
        if playbook_params is None:
            playbook_params = {}

        # Merge default params with playbook specific params
        playbook_full_params = self.ansible_vars_default | playbook_params
        ansible_result = ansible_runner.run(extravars=playbook_full_params, private_data_dir=self.ansible_dir,
                                            playbook=playbook_name)
        return ansible_result

# def run_bash_command(ansible_def_vars, data_dir, command):
#     print(data_dir)
#     print(command)
#     ansible_def_vars['command'] = command
#     r = ansible_runner.run(extravars=ansible_def_vars, private_data_dir=data_dir, playbook='generic_commands.yml')
#     print(r)
#     output = []
#
#     for event in r.events:
#         if 'event_data' in event:
#             if 'res' in event['event_data']:
#                 if 'cmd' in event['event_data']['res'] and len(event['event_data']['res']['cmd']) > 0:
#                     if event['event_data']['res']['cmd'][0] == command:
#                         output.append(event['event_data']['res']['stdout_lines'])
#
#     return output