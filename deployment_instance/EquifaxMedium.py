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
from ansible.vulnerabilities import SetupStrutsVulnerability
from ansible.goals import AddData
from ansible.caldera import InstallAttacker
from ansible.defender import InstallSysFlow

from .network import Network, Subnet
from .openstack.openstack_processor import get_hosts_on_subnet

from faker import Faker
import random

fake = Faker()


class EquifaxMedium(DeploymentInstance):
    def __init__(self, ansible_runner: AnsibleRunner, openstack_conn, caldera_ip):
        super().__init__(ansible_runner, openstack_conn, caldera_ip)
        self.topology = "equifax_medium"
        self.flags = {}
        self.root_flags = {}
        self.parse_network()

    def parse_network(self):
        self.webservers = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="webserver"
        )
        for host in self.webservers:
            host.users.append("tomcat")

        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]

        self.employee_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.201.0/24", host_name_prefix="employee"
        )
        for host in self.employee_hosts:
            username = host.name.replace("_", "")
            host.users.append(username)

        self.database_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.201.0/24", host_name_prefix="database"
        )
        for host in self.database_hosts:
            username = host.name.replace("_", "")
            host.users.append(username)

        webserverSubnet = Subnet("webserver_network", self.webservers, "webserver")
        corportateSubnet = Subnet(
            "critical_company_network",
            self.employee_hosts + self.database_hosts,
            "critical_company",
        )

        self.network = Network("equifax_network", [webserverSubnet, corportateSubnet])

    def compile_setup(self):
        log_event("Deployment Instace", "Setting up Equifax Instance")
        self.find_management_server(self.caldera_ip)
        self.parse_network()

        self.ansible_runner.run_playbook(CheckIfHostUp(self.webservers[0].ip))
        time.sleep(3)

        # Install all base packages
        self.ansible_runner.run_playbook(
            InstallBasePackages(
                self.network.get_all_host_ips() + [self.attacker_host.ip]
            )
        )

        # Install sysflow on all hosts
        self.ansible_runner.run_playbook(
            InstallSysFlow(self.network.get_all_host_ips())
        )

        # Setup apache struts and vulnerability
        webserver_ips = [host.ip for host in self.webservers]
        self.ansible_runner.run_playbook(SetupStrutsVulnerability(webserver_ips))

        # Setup users on corporte hosts
        for host in self.employee_hosts + self.database_hosts:
            for user in host.users:
                self.ansible_runner.run_playbook(CreateUser(host.ip, user, "ubuntu"))

        # Choose 3 random webservers to setup SSH keys
        webservers_with_creds = random.sample(self.webservers, 3)
        for webserver in webservers_with_creds:
            for employee in self.employee_hosts:
                self.ansible_runner.run_playbook(
                    SetupServerSSHKeys(
                        webserver.ip, "tomcat", employee.ip, employee.users[0]
                    )
                )
            for database in self.database_hosts:
                self.ansible_runner.run_playbook(
                    SetupServerSSHKeys(
                        webserver.ip, "tomcat", database.ip, database.users[0]
                    )
                )

        # Add data to database hosts
        i = 0
        for database in self.database_hosts:
            self.ansible_runner.run_playbook(
                AddData(database.ip, database.users[0], f"~/data_{database.name}.json")
            )

    def runtime_setup(self):
        # Setup attacker on intern machine
        self.ansible_runner.run_playbook(CreateSSHKey(self.attacker_host.ip, "root"))
        self.ansible_runner.run_playbook(
            InstallAttacker(self.attacker_host.ip, "root", self.caldera_ip)
        )
