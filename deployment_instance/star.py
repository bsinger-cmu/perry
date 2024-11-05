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
from ansible.vulnerabilities import SetupNetcatShell
from ansible.goals import AddData
from ansible.caldera import InstallAttacker
from ansible.defender import InstallSysFlow

from .network import Network, Subnet
from .openstack.openstack_processor import get_hosts_on_subnet

import config.Config as config

from faker import Faker
import random

fake = Faker()

NUMBER_RING_HOSTS = 25


class Star(DeploymentInstance):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config: config.Config,
        topology="star",
    ):
        super().__init__(ansible_runner, openstack_conn, caldera_ip, config)
        self.topology = topology
        self.flags = {}
        self.root_flags = {}

    def parse_network(self):
        self.star_hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="host"
        )

        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]

        ringSubnet = Subnet("ring_network", self.star_hosts, "employee_one_group")

        self.network = Network("ring_network", [ringSubnet])
        for host in self.network.get_all_hosts():
            username = host.name.replace("_", "")
            host.users.append(username)

        if len(self.network.get_all_hosts()) != NUMBER_RING_HOSTS:
            raise Exception(
                f"Number of hosts in network does not match expected number of hosts. Expected {NUMBER_RING_HOSTS} but got {len(self.network.get_all_hosts())}"
            )

    def compile_setup(self):
        log_event("Deployment Instace", "Setting up ICS network")
        self.find_management_server()
        self.parse_network()

        self.ansible_runner.run_playbook(CheckIfHostUp(self.star_hosts[0].ip))
        time.sleep(3)

        # Install all base packages
        self.ansible_runner.run_playbook(
            InstallBasePackages(
                self.network.get_all_host_ips() + [self.attacker_host.ip]
            )
        )

        # Install sysflow on all hosts
        self.ansible_runner.run_playbook(
            InstallSysFlow(self.network.get_all_host_ips(), self.config)
        )

        # Setup users on all hosts
        for host in self.network.get_all_hosts():
            for user in host.users:
                self.ansible_runner.run_playbook(CreateUser(host.ip, user, "ubuntu"))

        # Attacker host has all credentials
        for i, host in enumerate(self.star_hosts):
            action = SetupServerSSHKeys(
                self.attacker_host.ip,
                self.attacker_host.users[0],
                host.ip,
                host.users[0],
            )
            self.ansible_runner.run_playbook(action)

        # Add fake data to each host
        for host in self.network.get_all_hosts():
            self.ansible_runner.run_playbook(
                AddData(host.ip, host.users[0], f"~/data_{host.name}.json")
            )

    def runtime_setup(self):
        # Randomly choose 1 ring to have attacker
        initial_access = random.choice(self.star_hosts)

        # Setup attacker

        self.ansible_runner.run_playbook(
            InstallAttacker(initial_access.ip, initial_access.users[0], self.caldera_ip)
        )

        attacker_host = self.attacker_host
        self.ansible_runner.run_playbook(CreateSSHKey(attacker_host.ip, "root"))
        self.ansible_runner.run_playbook(
            InstallAttacker(attacker_host.ip, "root", self.caldera_ip)
        )
