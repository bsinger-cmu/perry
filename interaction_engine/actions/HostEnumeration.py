from .Action import Action
from openstack_helper_functions.network_helpers import servers_ips_on_subnet

class HostEnumeration(Action):
    def __init__(self):
        self.subnet = None

    def set_subnet_to_scan(self, subnet):
        self.subnet = subnet

    def run(self, env):
        if self.subnet is not None:
            return servers_ips_on_subnet(env.conn, self.subnet)
        else:
            raise Exception('No subnet is set to scan')
