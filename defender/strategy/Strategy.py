from defender.arsenal import CountArsenal
from defender.capabilities import Action
from defender.telemetry.events import HighLevelEvent
from deployment_instance.network import Network
from defender.orchestrator import Orchestrator
from utility.logging import get_logger


class Strategy(object):
    def __init__(
        self, arsenal: CountArsenal, network: Network, orchestrator: Orchestrator
    ):
        self.arsenal = arsenal
        self.network = network
        self.orchestrator = orchestrator
        self.logger = get_logger()

    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        return []
