from deployment_instance.network import Host
from defender.capabilities import (
    Action,
    DeployDecoy,
    AddHoneyCredentials,
)

from defender.orchestrator.openstack_actuators import (
    AddHoneyCredentials as AddHoneyCredentialsActuator,
)

from defender.telemetry.events import HighLevelEvent
from defender.strategy import Strategy

import random
from utility.logging import log_event


class LayeredOT(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("StaticLayered", "Initializing StaticLayered strategy")
        num_decoys = self.arsenal.storage["DeployDecoy"]
        num_honeycreds = self.arsenal.storage["HoneyCredentials"]

        ot_subnet = self.network.get_subnet_by_name("OT_network")

        if ot_subnet is None:
            log_event("StaticLayered", "Error could not find ot subnet")
            return []

        actions = []
        # Randomly deploy decoys on employee networks
        for i in range(0, num_decoys):
            decoy_name = f"decoy_{i}"
            # IP set by actuator
            decoy_host = Host(decoy_name, "")
            ot_subnet.add_host(decoy_host, decoy=True)

            decoy_action = DeployDecoy(
                sec_group=ot_subnet.sec_group,
                network=ot_subnet.name,
                server=decoy_name,
                host=decoy_host,
                apacheVulnerability=True,
            )
            actions.append(decoy_action)

        # Initialize decoys so we can setup fake credentials
        self.orchestrator.run(actions)

        # Split credentials between subnets
        credentialActions = []
        for i in range(0, num_honeycreds):
            deploy_host = ot_subnet.get_random_host()
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
