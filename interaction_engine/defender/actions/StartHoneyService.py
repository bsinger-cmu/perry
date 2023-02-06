from defender.actions import DefenderAction

class StartHoneyService(DefenderAction):

    def __init__(self, ansible_runner):
        super().__init__(ansible_runner)

    def run(self, host):
        params = {'host': host}
        self.ansible_runner.run_playbook('defender/deploy_honey_ssh.yml', playbook_params=params)