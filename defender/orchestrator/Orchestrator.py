class Orchestrator(object):

    def __init__(self, actuators: dict):
        self.actuators = actuators

    # Runs an action on your infrastructure
    def run(self, actions):

        # For each action
        for action in actions:
            # Find the correct actuator for the action
            actuator = self.actuators[action.Capability]

            # Run the action
            actuator.run(action)

        return