from deployment_instance.topology_orchestrator import deploy_network, destroy_network
from deployment_instance.vulnerability_orchestrator import VulnerabilityOrchestrator

public_ip = '10.20.20'
# Finds management server that can be used to talk to other servers
# Assumes only one server has floating ip and it is the management server
def find_manage_server(conn):
    for server in conn.compute.servers():
        for network, network_attrs in server.addresses.items():
            ip_addresses = [x['addr'] for x in network_attrs]
            for ip in ip_addresses:
                if public_ip in ip:
                    return server, ip
    return None, None
                
class DeploymentInstance:
    def __init__(self, ansible_runner, openstack_conn, caldera_ip):
        self.ansible_runner = ansible_runner
        self.openstack_conn = openstack_conn
        self.ssh_key_path = './environment/ssh_keys/'
        self.caldera_ip = caldera_ip
        self.vuln_orch = VulnerabilityOrchestrator(self.ansible_runner)

        self.flags = {}

        self.find_management_server()

    def find_management_server(self):
        manage_server, manage_ip = find_manage_server(self.openstack_conn)
        self.ansible_runner.update_management_ip(manage_ip)

    def check_flag(self, flag):
        if flag in self.flags:
            return self.flags[flag]
        return 0
    
    def deploy_topology(self):
        destroy_network(self.topology)
        deploy_network(self.topology)

    def setup_instance(self, already_deployed=False):
        if not already_deployed:
            self.deploy_topology()
        self.setup()
    
    def setup(self):
        return
