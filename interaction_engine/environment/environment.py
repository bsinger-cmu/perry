class Environment:
    attackers = []
    defenders = []

    def __init__(self):
        return

    def step(self):
        for attacker in self.attackers:
            attacker.step()
        for defender in self.defenders:
            defender.step()
        return
