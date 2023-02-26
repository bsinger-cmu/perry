from .OpenstackActuator import OpenstackActuator


class StartHoneyService(OpenstackActuator):

    def actuate(self, action):
        params = {'host': action.host}
        self.ansible_runner.run_playbook('defender/deploy_honey_ssh.yml', playbook_params=params)