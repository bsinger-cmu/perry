from .TelemetryServer import TelemetryServer

from flask import request

from queue import Queue

class Defender:

    def __init__(self, ansible_runner):
        self.telemetry_queue = Queue()
        self.ansible_runner = ansible_runner

    def start(self):
        # Start the telemetry server
        self.telemetry_server = TelemetryServer('TelemetryServer', self.HandleTelemetryEvent)
        self.telemetry_server.start()

    def HandleTelemetryEvent(self, event):
        self.telemetry_queue.put(event)

    def run(self):
        if not self.telemetry_queue.empty():
            event = self.telemetry_queue.get()
        else:
            event = None
        
        if event is not None:
            print('Got event: {}'.format(event))