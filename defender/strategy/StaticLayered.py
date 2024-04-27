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


class StaticLayered(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("StaticRandom", "Initializing StaticRandom strategy")
        num_decoys = self.arsenal.storage["DeployDecoy"]
        num_honeycreds = self.arsenal.storage["HoneyCredentials"]

        actions = []
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
        for i in range(0, num_honeycreds):
            deploy_host = self.network.get_random_host()
            target_host = self.network.get_random_decoy()

            # Add fake credentials to decoy
            self.orchestrator.run(
                [AddHoneyCredentials(deploy_host, target_host, 1, real=True)]
            )

        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        actions = []

        return actions
