from .Orchestrator import Orchestrator
from .openstack_actuators import ShutdownServer, StartHoneyService, DeployDecoy
from defender import capabilities

class OpenstackOrchestrator(Orchestrator):

    def __init__(self, openstack_conn, ansible_runner, external_elasticsearch_server, elasticsearch_api_key):
        self.openstack_conn = openstack_conn
        self.ansible_runner = ansible_runner

        self.external_elasticsearch_server = external_elasticsearch_server
        self.elasticsearch_api_key = elasticsearch_api_key
    
        actuators = {
            capabilities.ShutdownServer.name: ShutdownServer(self.openstack_conn, self.ansible_runner,
                                                             self.external_elasticsearch_server, self.elasticsearch_api_key),
            capabilities.StartHoneyService.name: StartHoneyService(self.openstack_conn, self.ansible_runner, 
                                                                   self.external_elasticsearch_server, self.elasticsearch_api_key),
            capabilities.DeployDecoy.name: DeployDecoy(self.openstack_conn, self.ansible_runner, 
                                                       self.external_elasticsearch_server, self.elasticsearch_api_key)
        }
                
        super().__init__(actuators)


    # Run actions on openstack
    def run(self, actions):
        for action in actions:
            self.actuators[action.name].actuate(action)
        return