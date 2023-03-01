from os import chmod
from Crypto.PublicKey import RSA
from deployment_instance import DeploymentInstance
from deployment_instance.SetupFlag import setup_flag
from deployment_instance.topology_orchestrator import deploy_network, destroy_network
import random

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
                
class TwoPathInstance(DeploymentInstance):
    def __init__(self, ansible_runner, openstack_conn):
        super().__init__(ansible_runner, openstack_conn)

    def find_management_server(self):
        manage_server, manage_ip = find_manage_server(self.openstack_conn)
        self.ansible_runner.update_management_ip(manage_ip)


    def setup(self):
        # Setup topology
        destroy_network('two_path_network')
        deploy_network('two_path_network')

        # Update management ip for new network
        # TODO have management server be fixed, and only deploy instance servers
        self.find_management_server()

        # Install ubuntu users on all servers
        params = {'host': '192.168.200.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        params = {'host': '192.168.201.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        params = {'host': '192.168.202.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        params = {'host': '192.168.203.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)

        # Enable vulnerability on flag and attacker server
        params = {'host': '192.168.200.3'}
        r = self.ansible_runner.run_playbook('vulnerabilities/sshEnablePasswordLogin.yml', playbook_params=params)
        params = {'host': '192.168.203.3'}
        r = self.ansible_runner.run_playbook('vulnerabilities/sshEnablePasswordLogin.yml', playbook_params=params)

        # Randomly choose A or B server to be vulnerable
        coin_flip = random.randint(0,1)
        if coin_flip == 0:
            params = {'host': '192.168.201.3'}
            r = self.ansible_runner.run_playbook('vulnerabilities/sshEnablePasswordLogin.yml', playbook_params=params)
        else:
            params = {'host': '192.168.202.3'}
            r = self.ansible_runner.run_playbook('vulnerabilities/sshEnablePasswordLogin.yml', playbook_params=params)

        # Install ssh pass on all servers
        # TODO maybe attacker has to do this?
        params = {'host': '192.168.200.3', 'package': 'sshpass'}
        r = self.ansible_runner.run_playbook('common/installPackage.yml', playbook_params=params)
        params = {'host': '192.168.201.3', 'package': 'sshpass'}
        r = self.ansible_runner.run_playbook('common/installPackage.yml', playbook_params=params)
        params = {'host': '192.168.202.3', 'package': 'sshpass'}
        r = self.ansible_runner.run_playbook('common/installPackage.yml', playbook_params=params)
        params = {'host': '192.168.203.3', 'package': 'sshpass'}
        r = self.ansible_runner.run_playbook('common/installPackage.yml', playbook_params=params)

        # Setup flag
        flag = setup_flag(self.ansible_runner, '192.168.203.3', '/home/ubuntu/flag.txt', 'ubuntu', 'root')
        self.flags = [flag]
