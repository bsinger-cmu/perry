from .Agent import Agent
from rich import print
from actions.HostEnumeration import HostEnumeration
from actions.PortEnumeration import PortEnumeration
from actions.Exploit import MetasploitExploit

# TODO Attacker agents shouldn't have access to openstack connections
class SimpleAttacker(Agent):
    def __init__(self):
        self.host_enumeration = HostEnumeration()
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

        # Set subnet to scan
        servers_on_subnet = self.host_enumeration.set_subnet_to_scan('192.168.199.0/24')
        # Tell environment to run action
        # Passing around self like this seems odd to me, not sure of better way tho
        res = env.run_action(self, self.host_enumeration)
        print(res)

        return