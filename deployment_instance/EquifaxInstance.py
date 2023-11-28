from deployment_instance import DeploymentInstance
import time
from utility.logging import log_event

from ansible.AnsibleRunner import AnsibleRunner
from ansible.AnsiblePlaybook import AnsiblePlaybook

from ansible.deployment_instance import (
    InstallBasePackages,
    CheckIfHostUp,
    SetupServerSSHKeys,
)
from ansible.common import CreateUser
from ansible.vulnerabilities import EquifaxSSHConfig


class EquifaxInstance(DeploymentInstance):
    def __init__(self, ansible_runner: AnsibleRunner, openstack_conn, caldera_ip):
        super().__init__(ansible_runner, openstack_conn, caldera_ip)
        self.topology = "equifax_network"
        self.flags = {}
        self.root_flags = {}

        self.flags["192.168.201.5"] = "database-A-user-flag"
        self.flags["192.168.201.6"] = "database-B-user-flag"

        self.root_flags["192.168.201.5"] = "database-A-root-flag"
        self.root_flags["192.168.201.6"] = "database-B-root-flag"

    def compile_setup(self):
        log_event("Deployment Instace", "Setting up Equifax Instance")
        self.find_management_server()

        self.ansible_runner.run_playbook(CheckIfHostUp("192.168.200.3"))

        time.sleep(3)

        # Install users on all hosts
        self.ansible_runner.run_playbook(
            CreateUser("192.168.200.3", "webserverA", "ubuntu")
        )
        self.ansible_runner.run_playbook(
            CreateUser("192.168.200.4", "webserverB", "ubuntu")
        )
        self.ansible_runner.run_playbook(
            CreateUser("192.168.200.5", "webserverC", "ubuntu")
        )

        # Employee host users
        self.ansible_runner.run_playbook(
            CreateUser("192.168.201.3", "employeeA", "ubuntu")
        )
        self.ansible_runner.run_playbook(
            CreateUser("192.168.201.4", "employeeB", "ubuntu")
        )
        self.ansible_runner.run_playbook(
            CreateUser("192.168.201.5", "databaseA", "ubuntu")
        )
        self.ansible_runner.run_playbook(
            CreateUser("192.168.201.6", "databaseB", "ubuntu")
        )

        # self.ansible_runner.run_playbook(
        #     InstallBasePackages(
        #         [
        #             "192.168.200.3",
        #             "192.168.200.4",
        #             "192.168.200.5",
        #             "192.168.201.3",
        #             "192.168.201.4",
        #             "192.168.201.5",
        #             "192.168.201.6",
        #             "192.168.202.3",
        #         ]
        #     )
        # )

        ssh_playbooks: list[AnsiblePlaybook] = [
            SetupServerSSHKeys(
                "192.168.200.5", "webserverC", "192.168.201.3", "employeeA"
            ),
            SetupServerSSHKeys(
                "192.168.200.5", "webserverC", "192.168.201.4", "employeeB"
            ),
            SetupServerSSHKeys(
                "192.168.200.5", "webserverC", "192.168.201.5", "databaseA"
            ),
            SetupServerSSHKeys(
                "192.168.200.5", "webserverC", "192.168.201.6", "databaseB"
            ),
        ]
        self.ansible_runner.run_playbooks(ssh_playbooks)

        self.ansible_runner.run_playbook(
            EquifaxSSHConfig("192.168.200.5", "webserverC")
        )

        # # Add vulnerabilities to hosts
        # # CEO
        # self.orchestrator.vulns.add_sshEnablePasswordLogin("192.168.201.3")
        # self.orchestrator.vulns.add_sshEnablePasswordLogin("192.168.201.4")
        # self.orchestrator.vulns.add_sshEnablePasswordLogin("192.168.201.5")
        # self.orchestrator.vulns.add_sshEnablePasswordLogin("192.168.201.6")

        # self.orchestrator.vulns.add_writeablePassword("192.168.201.5")
        # self.orchestrator.vulns.add_writeablePassword("192.168.201.6")

        # self.setup_flags()

    def setup_flags(self):
        self.orchestrator.goals.setup_flag(
            "192.168.201.5",
            "/home/database_A/flag.txt",
            self.flags["192.168.201.5"],
            "database_A",
            "root",
        )
        self.orchestrator.goals.setup_flag(
            "192.168.201.6",
            "/home/database_B/flag.txt",
            self.flags["192.168.201.6"],
            "database_B",
            "root",
        )

        for host in self.root_flags:
            self.orchestrator.goals.setup_root_flag(host, self.root_flags[host])

    def runtime_setup(self):
        # Execute Processes
        # self.orchestrator.vulns.run_vsftpdBackdoor('192.168.200.5')

        # Setup attacker on intern machine
        self.orchestrator.attacker.install_attacker(
            "192.168.200.7", "intern", self.caldera_ip
        )

        # TODO Start sysflow
