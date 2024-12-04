import time
from .OpenstackActuator import OpenstackActuator
from ansible.defender import DeployHoneyService
from defender import capabilities

from openstack_helper_functions.server_helpers import shutdown_server_by_ip


class StartHoneyService(OpenstackActuator):
    def actuate(self, action: capabilities.StartHoneyService):
        honey_service_pb = DeployHoneyService(
            action,
            self.external_elasticsearch_server,
            self.elasticsearch_api_key,
        )

        self.ansible_runner.run_playbook(honey_service_pb)
