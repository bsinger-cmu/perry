from actions.Action import Action
from .Resource import Resource
from .Credentials import Credentials

class Environment:
    attackers = []
    defenders = []

    attacker_hosts = {}

    def __init__(self, conn):
        self.conn = conn

        return

    def run_action(self, resource: Resource, action: Action, credentials: Credentials):
        return resource.run_action(action, credentials)

    def step(self):
        for attacker in self.attackers:
            attacker.step()
        for defender in self.defenders:
            defender.step()
        return
