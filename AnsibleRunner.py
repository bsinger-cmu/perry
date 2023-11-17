import ansible_runner
import argparse
from rich import print

from contextlib import redirect_stdout
from os import path


class AnsibleRunner:
    def __init__(self, ssh_key_path, management_ip, ansible_dir, log_path, quiet=False):
        self.ssh_key_path = ssh_key_path
        self.management_ip = management_ip
        self.ansible_dir = ansible_dir
        self.quiet = quiet
        self.log_path = log_path

        self.ansible_vars_default = {
            "manage_ip": self.management_ip,
            "ssh_key_path": self.ssh_key_path,
        }

    def run_playbook(self, playbook_name, playbook_params=None):
        if playbook_params is None:
            playbook_params = {}

        if self.quiet is False:
            print(f"\n")
            print(f"[RUNNING PLAYBOOK]    {playbook_name}")
            print(f"[PLAYBOOK  PARAMS]    {playbook_params}")

        log_path = path.join(self.log_path, "ansible_log.ansi")
        with open(log_path, "a") as f:
            with redirect_stdout(f):
                # Merge default params with playbook specific params
                playbook_full_params = self.ansible_vars_default | playbook_params
                ansible_result = ansible_runner.run(
                    extravars=playbook_full_params,
                    private_data_dir=self.ansible_dir,
                    playbook=playbook_name,
                    cancel_callback=lambda: None,
                    quiet=self.quiet,
                )
            if ansible_result.status == "failed":
                print(f"[PLAYBOOK  FAILED]    {playbook_name}")
                print(f"[PLAYBOOK  OUTPUT]    {ansible_result.stdout}")
                print(f"[PLAYBOOK  ERROR]     {ansible_result.stderr}")
                raise Exception(f"Playbook {playbook_name} failed")
        return ansible_result

    def update_management_ip(self, new_ip):
        self.management_ip = new_ip
        self.ansible_vars_default["manage_ip"] = new_ip
