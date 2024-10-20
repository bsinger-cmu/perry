from enum import Enum

from .Defender import Defender
from .capabilities import StartHoneyService, ShutdownServer, DeployDecoy
from .telemetry import SimpleTelemetryAnalysis

class WaitAndSpotDefender(Defender):

    def __init__(self, ansible_runner, openstack_conn, elasticsearch_conn, external_ip, elasticsearch_port, elasticsearch_api_key, arsenal):
        super().__init__(ansible_runner, openstack_conn, elasticsearch_conn, external_ip, elasticsearch_port, elasticsearch_api_key, arsenal)
        
        self.telemetry_analysis = SimpleTelemetryAnalysis(self.elasticsearch_conn)

    def start(self):
        self.deploy_telemetry()
        return
    
    def deploy_telemetry(self):
        # Deploy honey service
        honey_service_action = StartHoneyService('192.168.203.3')
        
        self.orchestrator.run([honey_service_action])
        return
    
    def run(self):
        new_events = self.telemetry_analysis.process_low_level_events()
        actions_to_execute = []

        for event in new_events:
            attacker_ip = event.attacker_ip
            print(f'Attacker found on {attacker_ip}, turning off host.')
            actions_to_execute.append(ShutdownServer(attacker_ip))

        self.orchestrator.run(actions_to_execute)

        return