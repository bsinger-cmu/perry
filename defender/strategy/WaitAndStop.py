from defender.arsenal import CountArsenal
from defender.capabilities import Action
from defender.capabilities import RestoreServer

from defender.telemetry.events import HighLevelEvent
from defender.telemetry.events import AttackerOnHost

from .setup.RandomPlacement import randomly_place_deception

from utility.logging import get_logger, log_event

# TODO - move this into the arsenal
hosts = [
    "192.168.200.3",
    "192.168.200.4",
    "192.168.200.5",
    "192.168.200.6",
    "192.168.200.7",
    "192.168.201.3",
]

networks = [
    {"network": "datacenter_network", "sec_group": "datacenter"},
    {"network": "company_network", "sec_group": "company"},
]


class WaitAndStop(object):
    arsenal: CountArsenal
    restore_count: int = 0
    max_restores: int = 0

    def __init__(self, arsenal: CountArsenal):
        self.arsenal = arsenal
        self.max_restores = self.arsenal.get_max_capability_count("RestoreServer")
        self.logger = get_logger()

    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("WaitAndStop", "Initializing WaitAndStop strategy")
        actions = randomly_place_deception(self.arsenal, hosts, networks)
        return actions

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
