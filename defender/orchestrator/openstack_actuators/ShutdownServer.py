from .OpenstackActuator import OpenstackActuator
from openstack_helper_functions.server_helpers import shutdown_server_by_ip


class ShutdownServer(OpenstackActuator):

    def actuate(self, action):
        shutdown_server_by_ip(self.openstack_conn, action.host_ip)