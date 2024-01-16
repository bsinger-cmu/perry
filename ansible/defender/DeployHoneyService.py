from ansible.AnsiblePlaybook import AnsiblePlaybook
from defender.capabilities import StartHoneyService


class DeployHoneyService(AnsiblePlaybook):
    def __init__(
        self,
        action: StartHoneyService,
        external_elasticsearch_server: str,
        elasticsearch_api_key: str,
    ) -> None:
        self.name = "defender/deploy_honey_service.yml"
        self.params = {
            "host": action.host,
            "port_no": action.port_no,
            "service": action.service,
            "elasticsearch_server": external_elasticsearch_server,
            "elasticsearch_api_key": elasticsearch_api_key,
        }
