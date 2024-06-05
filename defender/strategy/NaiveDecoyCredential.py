from defender.capabilities import (
    Action,
    AddHoneyCredentials,
)

from defender.orchestrator.openstack_actuators import (
    AddHoneyCredentials as AddHoneyCredentialsActuator,
)

from defender.telemetry.events import HighLevelEvent
from . import Strategy

from utility.logging import log_event


class NaiveDecoyCredential(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("StaticStandalone", "Initializing StaticStandalone strategy")
        num_honeycreds = self.arsenal.storage["HoneyCredentials"]

        # Add fake credentials to all hosts
        credential_actions = []
        credentials_per_subnet = int(num_honeycreds / len(self.network.subnets))
        for subnet in self.network.subnets:
            for i in range(0, credentials_per_subnet):
                deploy_host = subnet.get_random_host()
                target_host = self.network.get_random_host()
                credential_actions.append(
                    AddHoneyCredentials(deploy_host, target_host, 1, real=False)
                )

        # Add fake credentials to decoy
        AddHoneyCredentialsActuator.actuateMany(
            credential_actions, self.orchestrator.ansible_runner
        )

        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        actions = []

        return actions
