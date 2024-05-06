from deployment_instance.network import Host
from defender.capabilities import (
    Action,
    StartHoneyService,
    DeployDecoy,
    AddHoneyCredentials,
)

from defender.telemetry.events import HighLevelEvent
from . import Strategy

import random
from utility.logging import log_event


class StaticStandalone(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("StaticRandom", "Initializing StaticRandom strategy")
        num_honeyservice = self.arsenal.storage["HoneyService"]
        num_decoys = self.arsenal.storage["DeployDecoy"]
        num_honeycreds = self.arsenal.storage["HoneyCredentials"]

        ### Randomly deploy honey service hosts ###
        # Get hosts in network and shuffle them
        network_hosts = self.network.get_all_hosts()
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
            subnet_to_deploy = self.network.get_random_subnet()
            decoy_name = f"decoy_{i}"
            # IP set by actuator
            decoy_host = Host(decoy_name, "")
            subnet_to_deploy.add_host(decoy_host, decoy=True)

            decoy_action = DeployDecoy(
                sec_group=subnet_to_deploy.sec_group,
                network=subnet_to_deploy.name,
                server=decoy_name,
                host=decoy_host,
                apacheVulnerability=True,
            )
            actions.append(decoy_action)

        # Initialize decoys so we can setup fake credentials
        self.orchestrator.run(actions)

        # Add fake credentials to all hosts
        credentials_per_subnet = int(num_honeycreds / len(self.network.subnets))
        for subnet in self.network.subnets:
            for i in range(0, credentials_per_subnet):
                deploy_host = subnet.get_random_host()
                target_host = self.network.get_random_host()

                # Add fake credentials to decoy
                self.orchestrator.run(
                    [AddHoneyCredentials(deploy_host, target_host, 1, real=False)]
                )

        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        actions = []

        return actions
