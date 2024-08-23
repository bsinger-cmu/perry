from deployment_instance.network import Host
from defender.capabilities import (
    Action,
    StartHoneyService,
    DeployDecoy,
    AddHoneyCredentials,
)

from defender.orchestrator.openstack_actuators import (
    AddHoneyCredentials as AddHoneyCredentialsActuator,
)

from defender.telemetry.events import HighLevelEvent
from .. import Strategy

import random
from utility.logging import log_event


class RingTarpit(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("RingTarpit", "Initializing RingTarpit strategy")
        num_decoys = self.arsenal.storage["DeployDecoy"]
        num_honeycreds = self.arsenal.storage["HoneyCredentials"]

        ring_network = self.network.get_subnet_by_name("ring_network")
        if ring_network is None:
            raise Exception("Ring network not found")

        actions = []
        # Randomly deploy decoys on networks
        for i in range(0, num_decoys):
            decoy_name = f"decoy_{i}"
            # IP set by actuator
            decoy_host = Host(decoy_name, "")
            ring_network.add_host(decoy_host, decoy=True)

            decoy_action = DeployDecoy(
                sec_group=ring_network.sec_group,
                network=ring_network.name,
                server=decoy_name,
                host=decoy_host,
                apacheVulnerability=True,
            )
            actions.append(decoy_action)

        # Initialize decoys so we can setup fake credentials
        self.orchestrator.run(actions)

        # Half of credentials go to ring hosts
        credentialActions = []
        half_credentials = int(num_honeycreds / 2)
        for i in range(0, half_credentials):
            deploy_host = ring_network.get_random_host()
            target_host = self.network.get_random_decoy()

            # Add fake credentials to decoy
            credentialActions.append(
                AddHoneyCredentials(deploy_host, target_host, 1, real=True)
            )

        # Other half for intertwining decoys
        for i in range(0, half_credentials):
            deploy_host = self.network.get_random_decoy()
            target_host = self.network.get_random_decoy()

            # Add fake credentials to decoy
            credentialActions.append(
                AddHoneyCredentials(deploy_host, target_host, 1, real=True)
            )

        AddHoneyCredentialsActuator.actuateMany(
            credentialActions, self.orchestrator.ansible_runner
        )

        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        actions = []

        return actions
