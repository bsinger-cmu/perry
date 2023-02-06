from defender.actions import DefenderAction
from openstack_helper_functions.server_helpers import shutdown_server_by_name

class ShutdownServer(DefenderAction):

    def __init__(self, ansible_runner):
        super().__init__(ansible_runner)

    def run(self, host_name):
        shutdown_server_by_name(self.conn, host_name)