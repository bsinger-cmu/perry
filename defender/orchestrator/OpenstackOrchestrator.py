from .Orchestrator import Orchestrator
from .openstack_actuators import ShutdownServer, StartHoneyService
from defender import capabilities

class OpenstackOrchestrator(Orchestrator):

    def __init__(self, openstack_conn, ansible_runner):
        self.openstack_conn = openstack_conn
        self.ansible_runner = ansible_runner
    
        actuators = {
            capabilities.ShutdownServer.name: ShutdownServer(self.openstack_conn, self.ansible_runner),
            capabilities.StartHoneyService.name: StartHoneyService(self.openstack_conn, self.ansible_runner)
        }
                
        super().__init__(actuators)


    # Run actions on openstack
    def run(self, actions):
        for action in actions:
            self.actuators[action.name].actuate(action)
        return