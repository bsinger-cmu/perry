from defender.capabilities import Action
from openstack_helper_functions.server_helpers import shutdown_server_by_ip
from environment.network import Host


class DeployDecoy(Action):
    name = "deploy_decoy"

    def __init__(
        self,
        network: str,
        host: Host,
        server="decoy_host",
        sec_group="simple",
        image="Ubuntu20",
        flavor="p2.tiny",
        apacheVulnerability=False,
        honeySSHService=False,
    ):
        super().__init__()

        self.network = network
        self.server = server
        self.sec_group = sec_group
        self.image = image
        self.flavor = flavor
        self.host = host
        self.apacheVulnerability = apacheVulnerability
        self.honeySSHService = honeySSHService
