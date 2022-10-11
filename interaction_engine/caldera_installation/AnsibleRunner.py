import ansible_runner
import argparse
import ansible

class AnsibleRunner:
    def __init__(self, ssh_key, target_ip, ansible_dir):
        self.ssh_key_path = ssh_key
        self.management_ip = target_ip
        self.ansible_dir = ansible_dir
        self.ansible_vars_default = {'target_ip': self.management_ip, 'ssh_key_path': self.ssh_key_path}

    def run_playbook(self, playbook_name, playbook_params = None):

        if playbook_params is None:
            playbook_params = {}

        # Merge default params with playbook specific params
        playbook_full_params = self.ansible_vars_default | playbook_params
        ansible_result = ansible_runner.run(extravars=playbook_full_params, private_data_dir=self.ansible_dir, playbook=playbook_name)
        return ansible_result
