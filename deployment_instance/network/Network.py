from . import Subnet, Host
import random


class Network:
    def __init__(self, name: str, subnets: list[Subnet]):
        self.name = name
        self.subnets = subnets

    def get_all_hosts(self) -> list[Host]:
        hosts = []
        for subnet in self.subnets:
            hosts.extend(subnet.hosts)
        return hosts

    def get_all_host_ips(self) -> list[str]:
        return [host.ip for host in self.get_all_hosts()]

    def get_all_decoys(self) -> list[Host]:
        decoys = []
        for subnet in self.subnets:
            decoys.extend(subnet.decoys)
        return decoys

    def get_random_decoy(self) -> Host:
        return random.choice(self.get_all_decoys())

    def get_random_host(self) -> Host:
        return random.choice(self.get_all_hosts())

    def get_random_subnet(self) -> Subnet:
        return random.choice(self.subnets)

    def is_ip_decoy(self, ip: str):
        decoys = self.get_all_decoys()
        for decoy in decoys:
            if decoy.ip == ip:
                return True

        return False
