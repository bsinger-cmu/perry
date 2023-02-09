from defender.actions import DefenderAction
from openstack_helper_functions.server_helpers import shutdown_server_by_ip

class ShutdownServer(DefenderAction):

    def __init__(self, ansible_runner, openstack_conn):
        super().__init__(ansible_runner, openstack_conn)

    def run(self, host_ip):
        shutdown_server_by_ip(self.openstack_conn, host_ip)