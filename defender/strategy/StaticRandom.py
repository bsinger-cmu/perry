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
        randomly_place_deception(self.arsenal, self.network, self.orchestrator)
        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        actions = []

        return actions
