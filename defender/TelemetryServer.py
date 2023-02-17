# Simple server for receiving telemetry data
from flask import Flask, Response, request
import threading

host_name = "0.0.0.0"
port = 8887

class Event(object):
    def __init__(self, honey_type, service_type, attacker_host):
        self.honey_type = honey_type
        self.service_type = service_type
        self.attacker_host = attacker_host


class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response


class TelemetryServer(object):
    app = None

    def __init__(self, name, defender_cb):
        self.app = Flask(name)
        self.defender_cb = defender_cb
        self.app.add_url_rule('/alert', 'alert', EndpointAction(self.handle_alert), methods=['POST', 'GET'])
    
    def start(self):
        threading.Thread(target=lambda: self.app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

    def handle_alert(self):
        data = request.form
        honey_type = data['type']
        service_type = data['protocol']
        from_host = data['from_host']

        event = Event(honey_type, service_type, from_host)

        # Send this to defender
        self.defender_cb(event)

        return "Received!"