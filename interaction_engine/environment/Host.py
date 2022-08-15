from .Resource import Resource

class Host(Resource):
    name = ''
    ip = ''

    def __init__(self, name, ip):
        return