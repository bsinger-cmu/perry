from .orchestrator import OpenstackOrchestrator
from .arsenal import Arsenal
from .strategy import Strategy
from .telemetry import TelemetryAnalysis

from deployment_instance.network import Network

from queue import Queue


class Defender:
    strategy: Strategy
    telemetryAnalysis: TelemetryAnalysis
    arsenal: Arsenal
    orchestrator: OpenstackOrchestrator
    network: Network

    def __init__(
        self,
        arsenal: Arsenal,
        strategy: Strategy,
        telemetryAnalysis: TelemetryAnalysis,
        orchestrator: OpenstackOrchestrator,
        network: Network,
    ):
        self.metrics = {}
        self.arsenal = arsenal
        self.strategy = strategy
        self.telemetry_analysis = telemetryAnalysis
        self.orchestrator = orchestrator
        self.network = network

    def start(self):
        # Run initial strategy setup
        initial_actions = self.strategy.initialize()
        self.orchestrator.run(initial_actions)

    def run(self):
        # Process telemetry
        new_events = self.telemetry_analysis.process_low_level_events()
        # Run strategy
        actions = self.strategy.run(new_events)
        # Run strategy actions
        self.orchestrator.run(actions)
