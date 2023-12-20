from deployment_instance import DeploymentInstance
import time
from utility.logging import log_event

from ansible.AnsibleRunner import AnsibleRunner
from ansible.AnsiblePlaybook import AnsiblePlaybook

from ansible.deployment_instance import (
    InstallBasePackages,
    CheckIfHostUp,
    SetupServerSSHKeys,
    CreateSSHKey,
)
from ansible.common import CreateUser
from ansible.vulnerabilities import (
    EquifaxSSHConfig,
    SetupStrutsVulnerability,
)
from ansible.goals import AddData
from ansible.caldera import InstallAttacker


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

        self.ansible_runner.run_playbook(
            InstallBasePackages(
                [
                    "192.168.200.3",
                    "192.168.200.4",
                    "192.168.200.5",
                    "192.168.201.3",
                    "192.168.201.4",
                    "192.168.201.5",
                    "192.168.201.6",
                    "192.168.202.3",
                ]
            )
        )

        self.ansible_runner.run_playbook(SetupStrutsVulnerability("192.168.200.3"))
        self.ansible_runner.run_playbook(SetupStrutsVulnerability("192.168.200.4"))
        self.ansible_runner.run_playbook(SetupStrutsVulnerability("192.168.200.5"))

        ssh_playbooks: list[AnsiblePlaybook] = [
            SetupServerSSHKeys("192.168.200.5", "tomcat", "192.168.201.3", "employeeA"),
            SetupServerSSHKeys("192.168.200.5", "tomcat", "192.168.201.4", "employeeB"),
            SetupServerSSHKeys("192.168.200.5", "tomcat", "192.168.201.5", "databaseA"),
            SetupServerSSHKeys("192.168.200.5", "tomcat", "192.168.201.6", "databaseB"),
        ]
        self.ansible_runner.run_playbooks(ssh_playbooks)

        self.ansible_runner.run_playbook(EquifaxSSHConfig("192.168.200.5", "tomcat"))

        self.ansible_runner.run_playbook(
            AddData("192.168.201.5", "databaseA", "~/data1.json")
        )
        self.ansible_runner.run_playbook(
            AddData("192.168.201.6", "databaseB", "~/data2.json")
        )

        # Create SSH key for attacker
        self.ansible_runner.run_playbook(CreateSSHKey("192.168.202.3", "root"))

    def runtime_setup(self):
        # Execute Processes
        # self.orchestrator.vulns.run_vsftpdBackdoor('192.168.200.5')

        # Setup attacker on intern machine
        self.ansible_runner.run_playbook(
            InstallAttacker("192.168.202.3", "root", self.caldera_ip)
        )

        # TODO Start sysflow
