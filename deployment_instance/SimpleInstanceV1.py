from os import chmod
from Crypto.PublicKey import RSA
from deployment_instance import DeploymentInstance
from deployment_instance.SetupFlag import setup_flag
from deployment_instance.topology_orchestrator import deploy_network, destroy_network
import time

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
                
class SimpleInstanceV1(DeploymentInstance):
    def __init__(self, ansible_runner, openstack_conn):
        super().__init__(ansible_runner, openstack_conn)

        # Try to find management server early (for debugging)
        self.find_management_server()

    def find_management_server(self):
        manage_server, manage_ip = find_manage_server(self.openstack_conn)
        self.ansible_runner.update_management_ip(manage_ip)


    def setup(self, already_deployed=False):
        # Setup topology
        if not already_deployed:
            destroy_network('simple_multi_subnet')
            deploy_network('simple_multi_subnet')

        # Update management ip for new network
        # TODO have management server be fixed, and only deploy instance servers
        self.find_management_server()

        # Install sshpass for exploit
        params = {'host': '192.168.199.3', 'package': 'sshpass'}
        r = self.ansible_runner.run_playbook('common/installPackage.yml', playbook_params=params)

        # Setup user
        params = {'host': '192.168.199.4', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)

        # Setup flag
        flag = setup_flag(self.ansible_runner, '192.168.199.4', '/home/ubuntu/flag.txt', 'root', 'root')

        # Install priv escelation
        params = {'host': '192.168.199.4'}
        r = self.ansible_runner.run_playbook('vulnerabilities/writeablePasswd.yml', playbook_params=params)

        # Enable ssh passlogin
        params = {'host': '192.168.199.4'}
        r = self.ansible_runner.run_playbook('vulnerabilities/sshEnablePasswordLogin.yml', playbook_params=params)

        self.flags[flag] = 1
