from .TelemetryServer import TelemetryServer
from .orchestrator import OpenstackOrchestrator

from flask import request

from queue import Queue

class Defender:

    def __init__(self, ansible_runner, openstack_conn):
        self.telemetry_queue = Queue()
        self.orchestrator = OpenstackOrchestrator(openstack_conn, ansible_runner)

    def start(self):
        # Start the telemetry server
        self.telemetry_server = TelemetryServer('TelemetryServer', self.handle_telemetry_event)
        self.telemetry_server.start()

    def handle_telemetry_event(self, event):
        self.telemetry_queue.put(event)

    def run(self):
        if not self.telemetry_queue.empty():
            event = self.telemetry_queue.get()
        else:
            event = None
        
        if event is not None:
            print('Got event: {}'.format(event))