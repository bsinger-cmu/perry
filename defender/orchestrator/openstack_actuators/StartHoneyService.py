from .OpenstackActuator import OpenstackActuator


class StartHoneyService(OpenstackActuator):

    def actuate(self, action):
        params = {'host': action.host, 'elasticsearch_server': self.external_elasticsearch_server, 'elasticsearch_api_key': self.elasticsearch_api_key}
        print(params)
        self.ansible_runner.run_playbook('defender/deploy_honey_ssh.yml', playbook_params=params)