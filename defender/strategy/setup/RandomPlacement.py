import random

from defender.arsenal import CountArsenal
from defender.capabilities import StartHoneyService, DeployDecoy, AddHoneyCredentials
from defender.orchestrator import Orchestrator
from deployment_instance.network import Network, Host


def randomly_place_deception(
    arsenal: CountArsenal, network: Network, orchestrator: Orchestrator
):
    num_honeyservice = arsenal.storage["HoneyService"]
    num_decoys = arsenal.storage["DeployDecoy"]
    num_honeycreds = arsenal.storage["HoneyCredentials"]

    ### Randomly deploy honey service hosts ###
    # Get hosts in network and shuffle them
    network_hosts = network.get_all_hosts()
    random.shuffle(network_hosts)

    actions = []
    # For each honeyservice, deploy it on a host
    for i in range(0, num_honeyservice):
        # End if we run out of hosts
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

    # Initialize decoys so we can setup fake credentials
    orchestrator.run(actions)

    # Add fake credentials to all hosts
    if num_honeycreds != 0:
        for subnet in network.subnets:
            for host in subnet.hosts:
                decoy = network.get_random_decoy()
                # Add fake credentials to decoy
                orchestrator.run([AddHoneyCredentials(host, decoy, num_honeycreds)])
