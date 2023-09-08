import ansible_runner
import argparse
from rich import print

from contextlib import redirect_stdout


class AnsibleRunner:
    def __init__(self, ssh_key_path, management_ip, ansible_dir, quiet=False):
        self.ssh_key_path = ssh_key_path
        self.management_ip = management_ip
        self.ansible_dir = ansible_dir
        self.quiet = quiet

        self.ansible_vars_default = {
            'manage_ip': self.management_ip, 'ssh_key_path': self.ssh_key_path}

    def run_playbook(self, playbook_name, playbook_params=None):
        if playbook_params is None:
            playbook_params = {}

        if self.quiet is False:
            print(f"\n")
            print(f"[RUNNING PLAYBOOK]    {playbook_name}")
            print(f"[PLAYBOOK  PARAMS]    {playbook_params}")

        with open('logs/ansible_log.txt', 'a') as f:
            with redirect_stdout(f):
                # Merge default params with playbook specific params
                playbook_full_params = self.ansible_vars_default | playbook_params
                ansible_result = ansible_runner.run(extravars=playbook_full_params,
                                                    private_data_dir=self.ansible_dir,
                                                    playbook=playbook_name,
                                                    cancel_callback=lambda: None,
                                                    quiet=self.quiet)
            if ansible_result.status == "failed":
                print(f"[PLAYBOOK  FAILED]    {playbook_name}")
                print(f"[PLAYBOOK  OUTPUT]    {ansible_result.stdout}")
                print(f"[PLAYBOOK  ERROR]     {ansible_result.stderr}")
                raise Exception(f"Playbook {playbook_name} failed")
        return ansible_result

    def update_management_ip(self, new_ip):
        self.management_ip = new_ip
        self.ansible_vars_default['manage_ip'] = new_ip

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
