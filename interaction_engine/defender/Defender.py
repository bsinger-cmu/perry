from defender.TelemetryServer import TelemetryServer
from flask import request

from queue import Queue

class Defender:

    def __init__(self):
        self.telemetry_queue = Queue()
        return

    def start(self):
        # Start the telemetry server
        telemetry_server = TelemetryServer('TelemetryServer', self.HandleTelemetryEvent)
        telemetry_server.start()
        return

    def HandleTelemetryEvent(self, event):
        self.telemetry_queue.put(event)
        return

    def run(self):
        if not self.telemetry_queue.empty():
            event = self.telemetry_queue.get()
        else:
            event = None
        
        if event is not None:
            print('Got event: {}'.format(event))

        return
