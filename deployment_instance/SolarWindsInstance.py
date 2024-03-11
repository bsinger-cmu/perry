from deployment_instance import DeploymentInstance
import time
from utility.logging import log_event

from ansible.AnsibleRunner import AnsibleRunner
from ansible.AnsiblePlaybook import AnsiblePlaybook
import random

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

from .network import Network, Host, Subnet


class SolarWindsInstance(DeploymentInstance):
    def __init__(self, ansible_runner: AnsibleRunner, openstack_conn, caldera_ip):
        super().__init__(ansible_runner, openstack_conn, caldera_ip)
        self.topology = "solar_winds"
        self.flags = {}
        self.root_flags = {}

        self.flags["192.168.201.5"] = "database-A-user-flag"
        self.flags["192.168.201.6"] = "database-B-user-flag"

        self.root_flags["192.168.201.5"] = "database-A-root-flag"
        self.root_flags["192.168.201.6"] = "database-B-root-flag"

        webserverA = Host("webserverA", "192.168.200.4", ["tomcat"])
        webserverB = Host("webserverB", "192.168.200.5", ["tomcat"])
        webserverC = Host("webserverC", "192.168.200.6", ["tomcat"])

        userA = Host("user_A", "192.168.202.4", ["userA"])
        userB = Host("user_B", "192.168.202.5", ["userB"])
        userC = Host("user_C", "192.168.202.6", ["userC"])
        userD = Host("user_D", "192.168.202.7", ["userD"])

        databaseA = Host("database_A", "192.168.201.4", ["databaseA"])
        databaseB = Host("database_B", "192.168.201.5", ["databaseB"])

        self.webserverSubnet = Subnet(
            "webserver_network", [webserverA, webserverB, webserverC], "webserver"
        )
        self.corportateSubnet = Subnet(
            "company_network",
            [userA, userB, userC, userD],
            "critical_company",
        )
        self.criticalSubnet = Subnet(
            "critical_company_network",
            [databaseA, databaseB],
            "critical_company",
        )

        self.network = Network(
            "solarwinds_network",
            [self.webserverSubnet, self.corportateSubnet, self.criticalSubnet],
        )

    def compile_setup(self):
        log_event("Deployment Instace", "Setting up Equifax Instance")
        self.find_management_server()

        self.ansible_runner.run_playbook(CheckIfHostUp("192.168.200.4"))

        time.sleep(3)

        # Install users on all hosts
        self.ansible_runner.run_playbook(
            CreateUser("192.168.200.4", "webserverA", "ubuntu")
        )
        self.ansible_runner.run_playbook(
            CreateUser("192.168.200.5", "webserverB", "ubuntu")
        )
        self.ansible_runner.run_playbook(
            CreateUser("192.168.200.6", "webserverC", "ubuntu")
        )

        # Employee host users
        self.ansible_runner.run_playbook(CreateUser("192.168.202.4", "userA", "ubuntu"))
        self.ansible_runner.run_playbook(CreateUser("192.168.202.5", "userB", "ubuntu"))
        self.ansible_runner.run_playbook(CreateUser("192.168.202.6", "userC", "ubuntu"))
        self.ansible_runner.run_playbook(CreateUser("192.168.202.7", "userD", "ubuntu"))

        # Database host users
        self.ansible_runner.run_playbook(
            CreateUser("192.168.201.4", "databaseA", "ubuntu")
        )
        self.ansible_runner.run_playbook(
            CreateUser("192.168.201.5", "databaseB", "ubuntu")
        )

        self.ansible_runner.run_playbook(
            InstallBasePackages(
                [
                    "192.168.200.4",
                    "192.168.200.5",
                    "192.168.200.6",
                    "192.168.202.4",
                    "192.168.202.5",
                    "192.168.202.6",
                    "192.168.202.7",
                    "192.168.201.4",
                    "192.168.201.5",
                ]
            )
        )

        ssh_playbooks: list[AnsiblePlaybook] = [
            SetupServerSSHKeys("192.168.202.6", "userC", "192.168.201.4", "databaseA"),
            SetupServerSSHKeys("192.168.202.6", "userC", "192.168.201.5", "databaseB"),
        ]
        self.ansible_runner.run_playbooks(ssh_playbooks)

        self.ansible_runner.run_playbook(
            AddData("192.168.201.4", "databaseA", "~/data1.json")
        )
        self.ansible_runner.run_playbook(
            AddData("192.168.201.5", "databaseB", "~/data2.json")
        )

    def runtime_setup(self):

        hosts = random.shuffle(self.corportateSubnet.hosts)
        # randomly choose host
        infected_host = hosts[0]
        users = random.shuffle(infected_host.users)
        infected_user = users[0]

        # Setup attacker on intern machine
        self.ansible_runner.run_playbook(
            InstallAttacker(infected_host.ip, infected_user, self.caldera_ip)
        )
