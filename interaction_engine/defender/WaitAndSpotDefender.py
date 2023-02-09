from enum import Enum

from .Defender import Defender
from .actions.StartHoneyService import StartHoneyService
from .actions.ShutdownServer import ShutdownServer

class DefenderState(Enum):
    DEPLOY_TELEMETRY = 1
    WAIT_FOR_EVENT = 2
    REMOVE_ATTACKER = 3

class WaitAndSpotDefender(Defender):

    def __init__(self, ansible_runner, openstack_conn):
        super().__init__(ansible_runner, openstack_conn)

        self.state = DefenderState.DEPLOY_TELEMETRY
        
        # Initialize actions
        # TODO set all of this in a config file
        self.honey_service_action = StartHoneyService(self.ansible_runner, self.openstack_conn)
        self.shutdown_server_action = ShutdownServer(self.ansible_runner, self.openstack_conn)

    def run(self):
        if self.state == DefenderState.DEPLOY_TELEMETRY:
            self.deploy_telemetry()
        elif self.state == DefenderState.WAIT_FOR_EVENT:
            self.wait_for_event()
        elif self.state == DefenderState.REMOVE_ATTACKER:
            self.remove_attacker()

        return
    
    def deploy_telemetry(self):
        # Deploy honey service
        self.honey_service_action.run('192.168.200.3')

        self.state = DefenderState.WAIT_FOR_EVENT
        return
    
    def wait_for_event(self):
        if self.telemetry_queue.empty():
            return

        # If honeyservice event, shutdown server
        event = self.telemetry_queue.get()
        attacker_host = event.attacker_host

        print(f'Attacker found on {attacker_host}, turning off host.')
        self.shutdown_server_action.run(attacker_host)

        print('Got event: {}'.format(event))
        return
    
    def remove_attacker(self):
        return