from .Strategy import Strategy
from defender.capabilities import Action
from defender.telemetry.events import HighLevelEvent


class DoNothing(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        return []
