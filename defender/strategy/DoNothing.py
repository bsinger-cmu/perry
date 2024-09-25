from .Strategy import Strategy


class DoNothing(Strategy):
    # Run actions before the scenario starts
    def initialize(self):
        pass

    # Run actions during the scenario
    def run(self):
        pass
