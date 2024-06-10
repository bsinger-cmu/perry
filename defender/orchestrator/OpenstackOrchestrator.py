from .Orchestrator import Orchestrator
from .openstack_actuators import (
    ShutdownServer,
    StartHoneyService,
    AddHoneyCredentials,
    DeployDecoy,
    RestoreServer,
)
from defender import capabilities
from openstack.connection import Connection
from config.Config import Config
from deployment_instance.network import Network


class OpenstackOrchestrator(Orchestrator):
    def __init__(
        self,
        openstack_conn: Connection,
        ansible_runner,
        external_elasticsearch_server,
        elasticsearch_api_key,
        config: Config,
        network: Network,
    ):
        self.openstack_conn = openstack_conn
        self.ansible_runner = ansible_runner

        self.external_elasticsearch_server = external_elasticsearch_server
        self.elasticsearch_api_key = elasticsearch_api_key

        self.config = config
        self.network = network

        actuator_args = {
            "openstack_conn": self.openstack_conn,
            "ansible_runner": self.ansible_runner,
            "external_elasticsearch_server": self.external_elasticsearch_server,
            "elasticsearch_api_key": self.elasticsearch_api_key,
            "config": self.config,
            "network": self.network,
        }

        actuators = {
            capabilities.ShutdownServer.name: ShutdownServer(**actuator_args),
            capabilities.StartHoneyService.name: StartHoneyService(**actuator_args),
            capabilities.DeployDecoy.name: DeployDecoy(**actuator_args),
            capabilities.RestoreServer.name: RestoreServer(**actuator_args),
            capabilities.AddHoneyCredentials.name: AddHoneyCredentials(**actuator_args),
        }

        action_counts = {
            capabilities.ShutdownServer.name: 0,
            capabilities.StartHoneyService.name: 0,
            capabilities.DeployDecoy.name: 0,
            capabilities.RestoreServer.name: 0,
            capabilities.AddHoneyCredentials.name: 0,
        }

        super().__init__(actuators, action_counts)

    # Run actions on openstack
    def run(self, actions):
        for action in actions:
            self.actuators[action.name].actuate(action)

            if action.name in self.action_counts:
                self.action_counts[action.name] += 1
            else:
                self.action_counts[action.name] = 1
        return
