from defender.capabilities import Action
from openstack_helper_functions.server_helpers import shutdown_server_by_ip

class DeployDecoy(Action):

    name = 'deploy_decoy'
    
    def __init__(self, 
                 network: str, 
                 server="decoy_host", 
                 sec_group="simple", 
                 image="ubuntu20_sysflow", 
                 flavor="m1.small", 
                 keypair="cage"):
        super().__init__()

        self.network = network
        self.server = server  
        self.sec_group = sec_group
        self.image = image
        self.flavor = flavor 
        self.keypair = keypair