from defender.capabilities import Action
from defender.capabilities import AddHoneyCredentials

from defender.telemetry.events import Event
from . import Strategy

from .setup.RandomPlacement import randomly_place_deception

from utility.logging import log_event

import random


class StaticRandom(Strategy):
    # Run actions before the scenario starts
    def initialize(self):
        randomly_place_deception(self.arsenal, self.network, self.orchestrator)

    # Run actions during the scenario
    def run(self):
        pass
