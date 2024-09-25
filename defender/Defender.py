from .orchestrator import OpenstackOrchestrator
from .arsenal import Arsenal
from .strategy import Strategy
from .telemetry.telemetry_service import TelemetryService

from deployment_instance.network import Network

from .telemetry.telemetry_service import TelemetryService


class Defender:
    def __init__(
        self,
        arsenal: Arsenal,
        strategy: Strategy,
        telemetry_service: TelemetryService,
        orchestrator: OpenstackOrchestrator,
        network: Network,
    ):
        self.metrics = {}
        self.arsenal = arsenal
        self.strategy = strategy
        self.telemetry_service = telemetry_service
        self.orchestrator = orchestrator
        self.network = network

    def start(self):
        # Run initial strategy setup
        self.strategy.initialize()

    def run(self):
        # Process telemetry
        self.telemetry_service.process_telemetry()
        # Run strategy
        self.strategy.run()
