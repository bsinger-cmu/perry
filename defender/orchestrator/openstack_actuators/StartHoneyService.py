from .OpenstackActuator import OpenstackActuator


class StartHoneyService(OpenstackActuator):

    def actuate(self, action):
        # params = {'host': action.host, 'port_no': action.port_no, 'service': action.service, 'elasticsearch_server': self.external_elasticsearch_server, 'elasticsearch_api_key': self.elasticsearch_api_key}
        params = {'host': action.host, 'elasticsearch_server': self.external_elasticsearch_server, 'elasticsearch_api_key': self.elasticsearch_api_key}
        # self.ansible_runner.run_playbook('defender/deploy_honey_service.yml', playbook_params=params)
        self.ansible_runner.run_playbook('defender/deploy_honey_ssh.yml', playbook_params=params)