from .Orchestrator import Orchestrator
from .openstack_actuators import (
    ShutdownServer,
    StartHoneyService,
    AddHoneyCredentials,
    DeployDecoy,
    RestoreServer,
)
from defender import capabilities


class OpenstackOrchestrator(Orchestrator):
    def __init__(
        self,
        openstack_conn,
        ansible_runner,
        external_elasticsearch_server,
        elasticsearch_api_key,
    ):
        self.openstack_conn = openstack_conn
        self.ansible_runner = ansible_runner

        self.external_elasticsearch_server = external_elasticsearch_server
        self.elasticsearch_api_key = elasticsearch_api_key

        actuator_args = {
            "openstack_conn": self.openstack_conn,
            "ansible_runner": self.ansible_runner,
            "external_elasticsearch_server": self.external_elasticsearch_server,
            "elasticsearch_api_key": self.elasticsearch_api_key,
        }

        actuators = {
            capabilities.ShutdownServer.name: ShutdownServer(**actuator_args),
            capabilities.StartHoneyService.name: StartHoneyService(**actuator_args),
            capabilities.DeployDecoy.name: DeployDecoy(**actuator_args),
            capabilities.RestoreServer.name: RestoreServer(**actuator_args),
            capabilities.AddHoneyCredentials.name: AddHoneyCredentials(**actuator_args),
        }

        super().__init__(actuators)

    # Run actions on openstack
    def run(self, actions):
        for action in actions:
            self.actuators[action.name].actuate(action)
        return
