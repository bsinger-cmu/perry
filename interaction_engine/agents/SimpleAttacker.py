from .Agent import Agent
from rich import print
from actions.HostEnumeration import HostEnumeration

# TODO Attacker agents shouldn't have access to openstack connections
class SimpleAttacker(Agent):
    def __init__(self, conn):
        self.scanner = HostEnumeration(conn)
        return

    def step(self, env):
        # What servers do I have access to?
        compromised_servers = env.attacker_hosts[self]

        if len(compromised_servers) > 0:
            # What subnet is first server on?
            for network, network_attrs in compromised_servers[0].addresses.items():
                ip_addresses = [x['addr'] for x in network_attrs]

        # TODO automate this, many research ?? around this tho
        # Ip address of compromised host: 192.168.199.3
        # Subnet: 192.168.199.0/24
        servers_on_subnet = self.scanner.run('192.168.199.0/24')
        print(servers_on_subnet)

        return