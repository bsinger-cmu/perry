from .Resource import Resource

class NetworkService:
    def __init__(self, name, port):
        self.name = name
        self.port = port

        return

class Host(Resource):
    name = ''
    ip = ''
    network_services = []

    def __init__(self, name, ip, network_services):
        super().__init__()

        self.name = name
        self.ip = ip
        self.network_services = network_services

        return