class Action:

    def __init__(self):
        self.foothold = None
        self.target_host = None
        self.credential = None

    def run(self, env):
        """
        Input: 
            action
            resource to run the action on
            credentials to the resource
        Output:
            action result
        """
        return