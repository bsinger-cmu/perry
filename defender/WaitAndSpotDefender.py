from enum import Enum

from .Defender import Defender
from .capabilities.StartHoneyService import StartHoneyService
from .capabilities.ShutdownServer import ShutdownServer


class WaitAndSpotDefender(Defender):

    def __init__(self, ansible_runner, openstack_conn):
        super().__init__(ansible_runner, openstack_conn)
        
        # Initialize actions
        # TODO set all of this in a config file
        # self.honey_service_action = StartHoneyService(self.ansible_runner, self.openstack_conn)

    def start(self):
        super().start()
        self.deploy_telemetry()
    
    def run(self):
        #self.wait_for_event()
        return
    
    def deploy_telemetry(self):
        # Deploy honey service
        # self.honey_service_action.run('192.168.199.4')
        honey_service_action = ShutdownServer('192.168.199.3')
        self.orchestrator.run([honey_service_action])

        return

    def wait_for_event(self):
        if self.telemetry_queue.empty():
            return

        # If honeyservice event, shutdown server
        event = self.telemetry_queue.get()
        attacker_host = event.attacker_host

        print(f'Attacker found on {attacker_host}, turning off host.')
        self.shutdown_server_action.run(attacker_host)

        return
    