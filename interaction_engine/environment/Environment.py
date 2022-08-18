from actions.Action import Action

class Environment:
    attackers = []
    defenders = []

    attacker_hosts = {}

    def __init__(self, conn):
        self.conn = conn

        return

    def run_action(self, agent, action: Action):
        return action.run(self)

    def step(self):
        for attacker in self.attackers:
            attacker.step()
        for defender in self.defenders:
            defender.step()
        return
