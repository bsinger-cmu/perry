class Strategy(object):
    
    # Run actions before the scenario starts
    def initialize(self):
        return []

    # Run actions during the scenario
    def run(self, high_level_events):
        return []