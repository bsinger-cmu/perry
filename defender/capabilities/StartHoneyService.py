from defender.capabilities import Action

class StartHoneyService(Action):

    name = 'start_honey_service'
    
    def __init__(self, host):
        super().__init__()

        self.host = host