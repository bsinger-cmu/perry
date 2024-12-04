from defender.capabilities import Action

class StartHoneyService(Action):

    name = 'start_honey_service'
    
    def __init__(self, host, port_no='8000', service='ssh'):
        super().__init__()

        self.host = host
        self.port_no = port_no
        self.service = service