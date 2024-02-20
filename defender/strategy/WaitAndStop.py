from defender.capabilities import Action
from defender.capabilities import RestoreServer

from defender.telemetry.events import HighLevelEvent
from defender.telemetry.events import AttackerOnHost
from . import Strategy

from .setup.RandomPlacement import randomly_place_deception

from utility.logging import get_logger, log_event


class WaitAndStop(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("WaitAndStop", "Initializing WaitAndStop strategy")

        # Place deception
        randomly_place_deception(self.arsenal, self.network, self.orchestrator)

        # Get max restores
        self.restore_count = 0
        self.max_restores = self.arsenal.storage["RestoreServer"]

        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        actions = []

        # Process events
        for event in new_events:
            if isinstance(event, AttackerOnHost):
                log_event("Found attacker", f"Attacker on host {event.attacker_ip}")
                if self.max_restores == -1 or self.restore_count < self.max_restores:
                    # Restore host if attacker is detected
                    attacker_ip = event.attacker_ip
                    restoreAction = RestoreServer(attacker_ip)
                    actions.append(restoreAction)
                    self.restore_count += 1

        return actions
