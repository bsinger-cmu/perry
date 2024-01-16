from . import Subnet, Host


class Network:
    def __init__(self, name: str, subnets: list[Subnet]):
        self.name = name
        self.subnets = subnets

    def get_all_hosts(self) -> list[Host]:
        hosts = []
        for subnet in self.subnets:
            hosts.extend(subnet.hosts)
        return hosts
