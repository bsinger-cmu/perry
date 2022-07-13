from openstack_helper_functions.network_helpers import servers_ips_on_subnet

class SimpleScan:
    def __init__(self, conn):
        self.conn = conn

    def run(self, subnet):
        return servers_ips_on_subnet(self.conn, subnet)
