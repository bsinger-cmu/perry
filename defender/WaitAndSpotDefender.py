from enum import Enum

from .Defender import Defender
from .capabilities import StartHoneyService, ShutdownServer, DeployDecoy


class WaitAndSpotDefender(Defender):

    def __init__(self, ansible_runner, openstack_conn):
        super().__init__(ansible_runner, openstack_conn)

    def start(self):
        super().start()
        #self.deploy_telemetry()
    
    def run(self):
        #self.wait_for_event()

        print('Deploying decoy')
        test = DeployDecoy('internal_network')
        self.orchestrator.run([test])

        return
    
    def deploy_telemetry(self):
        # Deploy honey service
        honey_service_action = StartHoneyService('192.168.199.4')
        
        self.orchestrator.run([honey_service_action])
        return

    def wait_for_event(self):
        if self.telemetry_queue.empty():
            return

        # If honeyservice event, shutdown server
        event = self.telemetry_queue.get()
        attacker_host = event.attacker_host

        print(f'Attacker found on {attacker_host}, turning off host.')
        
        shutdown_server_action = ShutdownServer(attacker_host)

        self.orchestrator.run([shutdown_server_action])
        return
    