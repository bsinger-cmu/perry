import random

from defender.arsenal import CountArsenal
from defender.capabilities import StartHoneyService, DeployDecoy


def randomly_place_deception(arsenal: CountArsenal, hosts, networks):
    num_honeyservice = arsenal.storage["HoneyService"]
    num_decoys = arsenal.storage["DeployDecoy"]

    # Randomly deploy honey service hosts
    random.shuffle(hosts)
    actions = []
    for i in range(0, num_honeyservice):
        actions.append(StartHoneyService(hosts[i]))

    # Randomly deploy decoys on networks
    for i in range(0, num_decoys):
        random.shuffle(networks)
        network_to_deploy = networks[0]
        decoy_name = f"decoy_{i}"

        decoy_action = DeployDecoy(
            sec_group=network_to_deploy["sec_group"],
            network=network_to_deploy["network"],
            server=decoy_name,
        )

        actions.append(decoy_action)

    return actions
