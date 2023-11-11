from defender.arsenal import Arsenal
from defender.capabilities import Action
from defender.telemetry.events import HighLevelEvent


class Strategy(object):
    arsenal: Arsenal

    def __init__(self, arsenal: Arsenal):
        self.arsenal = arsenal

    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        return []
