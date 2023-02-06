from enum import Enum

from .Defender import Defender
from .actions.StartHoneyService import StartHoneyService, ShutdownServer

class DefenderState(Enum):
    DEPLOY_TELEMETRY = 1
    WAIT_FOR_EVENT = 2
    REMOVE_ATTACKER = 3

class WaitAndSpotDefender(Defender):

    def __init__(self, ansible_runner):
        super().__init__(ansible_runner)

        self.state = DefenderState.DEPLOY_TELEMETRY
        
        # Initialize actions
        # TODO set all of this in a config file
        self.honey_service_action = StartHoneyService(self.ansible_runner)
        self.shutdown_server_action = ShutdownServer(self.ansible_runner)

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
        self.honey_service_action.run('192.168.199.3')

        self.state = DefenderState.WAIT_FOR_EVENT
        return
    
    def wait_for_event(self):
        if self.telemetry_queue.empty():
            return
            
        event = self.telemetry_queue.get()
        print('Got event: {}'.format(event))

        return
    
    def remove_attacker(self):
        return