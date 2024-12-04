import time
from utility.logging import log_event

from ansible.AnsibleRunner import AnsibleRunner
from ansible.AnsiblePlaybook import AnsiblePlaybook

from ansible.deployment_instance import (
    InstallBasePackages,
    CheckIfHostUp,
    SetupServerSSHKeys,
    CreateSSHKey,
    InstallKaliPackages,
)
from ansible.common import CreateUser
from ansible.vulnerabilities import SetupStrutsVulnerability, SetupSudoEdit
from ansible.goals import AddData
from ansible.defender import InstallSysFlow
from ansible.caldera import InstallAttacker

from environment.environment import Environment
from environment.network import Network, Subnet
from environment.openstack.openstack_processor import get_hosts_on_subnet

import config.Config as config

from faker import Faker
import random

fake = Faker()


class EnterpriseB(Environment):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config: config.Config,
        topology="enterprise_b",
        number_of_hosts=40,
    ):
        super().__init__(ansible_runner, openstack_conn, caldera_ip, config)
        self.topology = topology
        self.flags = {}
        self.root_flags = {}
        self.number_of_hosts = number_of_hosts

    def parse_network(self):
        self.webservers = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="webserver"
        )
        self.employee_a_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.201.0/24", host_name_prefix="employee_a"
        )
        self.employee_b_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.204.0/24", host_name_prefix="employee_b"
        )
        self.employee_hosts = self.employee_a_hosts + self.employee_b_hosts
        self.databases = get_hosts_on_subnet(
            self.openstack_conn, "192.168.203.0/24", host_name_prefix="database"
        )
        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]

        for host in self.webservers:
            host.users.append("tomcat")

        for host in self.employee_hosts:
            username = host.name.replace("_", "")
            host.users.append(username)

        for host in self.databases:
            username = host.name.replace("_", "")
            host.users.append(username)

        branch_one_subnet = Subnet("branch_one", self.webservers, "talk_to_manage")
        branch_two_subnet = Subnet(
            "branch_two", self.employee_a_hosts, "talk_to_manage"
        )
        branch_three_subnet = Subnet("branch_three", self.databases, "talk_to_manage")
        employee_b_subnet = Subnet(
            "employee_b", self.employee_b_hosts, "talk_to_manage"
        )

        self.network = Network(
            "enterprise_b_network",
            [
                branch_one_subnet,
                branch_two_subnet,
                branch_three_subnet,
                employee_b_subnet,
            ],
        )

        if len(self.network.get_all_hosts()) != self.number_of_hosts:
            raise Exception(
                f"Number of hosts in network does not match expected number of hosts. Expected {self.number_of_hosts} but got {len(self.network.get_all_hosts())}"
            )

    def compile_setup(self):
        log_event("Deployment Instace", "Setting up Equifax Instance")
        self.find_management_server()
        self.parse_network()

        self.ansible_runner.run_playbook(CheckIfHostUp(self.attacker_host.ip))
        time.sleep(3)

        # Install all base packages
        self.ansible_runner.run_playbook(
            InstallBasePackages(self.network.get_all_host_ips())
        )
        self.ansible_runner.run_playbook(InstallKaliPackages(self.attacker_host.ip))

        # Install sysflow on all hosts
        self.ansible_runner.run_playbook(
            InstallSysFlow(self.network.get_all_host_ips(), self.config)
        )

        # Setup other users on all hosts
        for host in self.network.get_all_hosts():
            for user in host.users:
                self.ansible_runner.run_playbook(CreateUser(host.ip, user, "ubuntu"))
        for host in self.webservers:
            self.ansible_runner.run_playbook(CreateSSHKey(host.ip, host.users[0]))

        # Setup apache struts and vulnerability
        webserver_ips = [host.ip for host in self.webservers]
        self.ansible_runner.run_playbook(SetupStrutsVulnerability(webserver_ips))

        # Each web server has access to a random employee host
        random_access_hosts = random.sample(self.employee_hosts, len(self.webservers))
        for i in range(len(self.webservers)):
            self.ansible_runner.run_playbook(
                SetupServerSSHKeys(
                    self.webservers[i].ip,
                    self.webservers[i].users[0],
                    random_access_hosts[i].ip,
                    random_access_hosts[i].users[0],
                )
            )

        # A random employee host has access to all databases
        random_employee_host = random.choice(self.employee_hosts)
        for db in self.databases:
            self.ansible_runner.run_playbook(
                SetupServerSSHKeys(
                    random_employee_host.ip,
                    "root",
                    db.ip,
                    db.users[0],
                )
            )
        employee_host_ips = [host.ip for host in self.employee_hosts]
        self.ansible_runner.run_playbook(SetupSudoEdit(employee_host_ips))

        # Add data to database hosts
        for database in self.databases:
            self.ansible_runner.run_playbook(
                AddData(database.ip, database.users[0], f"~/data_{database.name}.json")
            )

    def runtime_setup(self):
        self.ansible_runner.run_playbook(
            InstallAttacker(self.attacker_host.ip, "root", self.caldera_ip)
        )