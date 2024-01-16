from defender.capabilities import Action
from defender.capabilities import AddHoneyCredentials

from defender.telemetry.events import HighLevelEvent
from . import Strategy

from .setup.RandomPlacement import randomly_place_deception

from utility.logging import log_event

import random


class StaticRandom(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("StaticRandom", "Initializing StaticRandom strategy")

        decoy_actions = randomly_place_deception(self.arsenal, self.network)
        # Initialize decoys so we can setup fake credentials
        self.orchestrator.run(decoy_actions)

        for subnet in self.network.subnets:
            if len(subnet.decoys) > 0:
                random.shuffle(subnet.decoys)
                random.shuffle(subnet.hosts)

                decoy = subnet.decoys[0]
                host = subnet.hosts[0]

                # Add fake credentials to decoy
                self.orchestrator.run([AddHoneyCredentials(host, decoy)])

        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        actions = []

        return actions
