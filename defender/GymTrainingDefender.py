from .Defender import Defender
from .capabilities import StartHoneyService, ShutdownServer, DeployDecoy
from .telemetry import SimpleTelemetryAnalysis


class OpenAIGYMTrainingDefender(Defender):

    def __init__(self, ansible_runner, openstack_conn, elasticsearch_conn, external_ip, elasticsearch_port, elasticsearch_api_key):
        super().__init__(ansible_runner, openstack_conn, elasticsearch_conn, external_ip, elasticsearch_port, elasticsearch_api_key)
        
        self.telemetry_analysis = SimpleTelemetryAnalysis(self.elasticsearch_conn)

    def start(self):
        super().start()
        self.deploy_telemetry()
    
    # Special run command that takes in actions from the gym
    def run(self, actions: list):
        # Run actions
        self.orchestrator.run(actions)

        # Return new events
        new_events = self.telemetry_analysis.process_low_level_events()
        return new_events
    