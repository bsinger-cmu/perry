import time

from ansible.AnsibleRunner import AnsibleRunner

from ansible.deployment_instance import (
    CheckIfHostUp,
)
from ansible.common import CreateUser
from ansible.caldera import InstallAttacker
from ansible.vulnerabilities import SetupSudoEdit, SetupWriteableSudoers

from environment.environment import Environment
from environment.network import Network, Subnet
from environment.openstack.openstack_processor import get_hosts_on_subnet

import config.Config as config

NUMBER_RING_HOSTS = 4


class DevEnvironment(Environment):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
        config: config.Config,
        topology="openstack_dev",
    ):
        super().__init__(ansible_runner, openstack_conn, caldera_ip, config)
        self.topology = topology
        self.flags = {}
        self.root_flags = {}

    def parse_network(self):
        self.hosts = get_hosts_on_subnet(
            self.openstack_conn, "192.168.200.0/24", host_name_prefix="host"
        )

        for host in self.hosts:
            if host.name == "host_1":
                self.privledge_box = host

        self.attacker_host = get_hosts_on_subnet(
            self.openstack_conn, "192.168.202.0/24", host_name_prefix="attacker"
        )[0]

        dev_subnet = Subnet("dev_hosts", self.hosts, "dev_hosts")
        attacker_subnet = Subnet("attacker", [self.attacker_host], "attacker")

        self.network = Network("ring_network", [dev_subnet, attacker_subnet])
        for host in self.network.get_all_hosts():
            username = host.name.replace("_", "")
            host.users.append(username)

        if len(self.network.get_all_hosts()) != NUMBER_RING_HOSTS:
            raise Exception(
                f"Expected number of hosts mismatch. Expected {NUMBER_RING_HOSTS} but got {len(self.network.get_all_hosts())}"
            )

    def compile_setup(self):
        self.find_management_server()
        self.parse_network()

        self.ansible_runner.run_playbook(CheckIfHostUp(self.hosts[0].ip))
        time.sleep(3)

        # Install all base packages
        # self.ansible_runner.run_playbook(
        #     InstallBasePackages(
        #         self.network.get_all_host_ips() + [self.attacker_host.ip]
        #     )
        # )

        # Setup a privledge vulnerability
        self.ansible_runner.run_playbook(SetupSudoEdit(self.privledge_box.ip))
        # self.ansible_runner.run_playbook(SetupWriteableSudoers(self.privledge_box.ip))

        # Setup users on all hosts
        for host in self.network.get_all_hosts():
            if host.name == "attacker":
                continue
            for user in host.users:
                self.ansible_runner.run_playbook(CreateUser(host.ip, user, "ubuntu"))

    def runtime_setup(self):
        # Setup attacker
        # attacker_host = self.attacker_host
        # self.ansible_runner.run_playbook(CreateSSHKey(attacker_host.ip, "root"))
        # self.ansible_runner.run_playbook(
        #     InstallAttacker(attacker_host.ip, "root", self.caldera_ip)
        # )

        # Priv box host
        self.ansible_runner.run_playbook(
            InstallAttacker(self.privledge_box.ip, "host1", self.caldera_ip)
        )
