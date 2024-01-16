import random

from defender.arsenal import CountArsenal
from defender.capabilities import StartHoneyService, DeployDecoy, AddHoneyCredentials

from deployment_instance.network import Network, Host


def randomly_place_deception(arsenal: CountArsenal, network: Network):
    num_honeyservice = arsenal.storage["HoneyService"]
    num_decoys = arsenal.storage["DeployDecoy"]

    # Randomly deploy honey service hosts
    network_hosts = network.get_all_hosts()
    random.shuffle(network_hosts)

    actions = []
    for i in range(0, num_honeyservice):
        if i >= len(network_hosts):
            break

        actions.append(StartHoneyService(network_hosts[i].ip))

    # Randomly deploy decoys on networks
    for i in range(0, num_decoys):
        random.shuffle(network.subnets)
        subnet_to_deploy = network.subnets[0]
        decoy_name = f"decoy_{i}"
        # IP set by actuator
        decoy_host = Host(decoy_name, "")
        subnet_to_deploy.add_host(decoy_host, decoy=True)

        decoy_action = DeployDecoy(
            sec_group=subnet_to_deploy.sec_group,
            network=subnet_to_deploy.name,
            server=decoy_name,
            host=decoy_host,
        )
        actions.append(decoy_action)

    return actions
