from .orchestrator import OpenstackOrchestrator

from queue import Queue

class Defender:

    def __init__(self, ansible_runner, openstack_conn, elasticsearch_conn, external_ip, elasticsearch_port, elasticsearch_api_key, arsenal):
        self.telemetry_queue = Queue()
        
        self.elasticsearch_conn = elasticsearch_conn
        self.external_ip = external_ip
        self.elasticsearch_port = elasticsearch_port
        self.elasticsearch_api_key = elasticsearch_api_key
        self.external_elasticsearch_server = f"https://{self.external_ip}:{self.elasticsearch_port}"

        self.orchestrator = OpenstackOrchestrator(openstack_conn, ansible_runner, self.external_elasticsearch_server, self.elasticsearch_api_key)

        self.arsenal = arsenal
        self.metrics = {}

    def start(self):
        return

    def handle_telemetry_event(self, event):
        self.telemetry_queue.put(event)
    
    def run(self):
        if not self.telemetry_queue.empty():
            event = self.telemetry_queue.get()
        else:
            event = None
        
        if event is not None:
            print('Got event: {}'.format(event))