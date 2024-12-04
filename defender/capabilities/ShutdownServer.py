from defender.capabilities import Action
from openstack_helper_functions.server_helpers import shutdown_server_by_ip

class ShutdownServer(Action):

    name = 'shutdown_server'
    
    def __init__(self, host_ip):
        super().__init__()

        self.host_ip = host_ip