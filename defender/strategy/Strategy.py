from defender.arsenal import CountArsenal
from deployment_instance.network import Network
from defender.orchestrator import Orchestrator
from utility.logging import get_logger
from defender.telemetry.telemetry_service import TelemetryService

from abc import ABC, abstractmethod


class Strategy(ABC):
    def __init__(
        self,
        arsenal: CountArsenal,
        network: Network,
        orchestrator: Orchestrator,
        telemetry_service: TelemetryService,
    ):
        self.arsenal = arsenal
        self.network = network
        self.orchestrator = orchestrator
        self.telemetry_service = telemetry_service
        self.logger = get_logger()

    # Run actions before the scenario starts
    @abstractmethod
    def initialize(self):
        pass

    # Run actions during the scenario
    @abstractmethod
    def run(self):
        pass
