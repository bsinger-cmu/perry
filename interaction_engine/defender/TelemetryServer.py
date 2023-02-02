# Simple server for receiving telemetry data
from flask import Flask, Response, request
import threading

host_name = "localhost"
port = 8001


class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response


class FlaskAppWrapper(object):
    app = None

    def __init__(self, name):
        self.app = Flask(name)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=methods)

def handle_alert():
    data = request.form
    honey_type = data['type']
    service_type = data['protocol']

    # ToDo send this to defender
    return "Received!"


if __name__ == '__main__':
    server = FlaskAppWrapper('TelemetryServer')
    server.add_endpoint(endpoint='/alert', endpoint_name='ad', handler=handle_alert, methods=['POST', 'GET'])

    threading.Thread(target=lambda: server.app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()