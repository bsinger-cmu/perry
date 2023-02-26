from defender.capabilities import Action
from openstack_helper_functions.server_helpers import shutdown_server_by_ip

class DeployDecoy(Action):

    name = 'deploy_decoy'
    
    def __init__(self, network):
        super().__init__()

        self.network = network