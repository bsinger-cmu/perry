from os import chmod
from Crypto.PublicKey import RSA
from deployment_instance import DeploymentInstance
from deployment_instance.SetupFlag import setup_flag
from deployment_instance.topology_orchestrator import deploy_network, destroy_network
import time
                
class SimpleInstanceV1(DeploymentInstance):

    def setup_attacker(self):
        # Setup initial attacker
        params = {'host': '192.168.199.3', 'user': 'ubuntu', 'caldera_ip': self.caldera_ip}
        self.ansible_runner.run_playbook('caldera/install_attacker.yml', playbook_params=params)


    def setup(self, already_deployed=False):
        # Setup topology
        if not already_deployed:
            destroy_network('simple_multi_subnet')
            deploy_network('simple_multi_subnet')
            time.sleep(5)

        # Update management ip for new network
        # TODO have management server be fixed, and only deploy instance servers
        self.find_management_server()

        # Check if host is up
        params = {'host': '192.168.199.3'}
        r = self.ansible_runner.run_playbook('deployment_instance/check_if_host_up.yml', playbook_params=params)

        time.sleep(3)

        # Install base dependencies
        params = {'host': '192.168.199.3'}
        r = self.ansible_runner.run_playbook('deployment_instance/install_base_packages.yml', playbook_params=params)
        params = {'host': '192.168.199.4'}
        r = self.ansible_runner.run_playbook('deployment_instance/install_base_packages.yml', playbook_params=params)

        # Setup attacker
        self.setup_attacker()

        # Setup user
        params = {'host': '192.168.199.4', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)

        # Setup flag
        self.flags['192.168.199.3'] = setup_flag(self.ansible_runner, '192.168.199.3', '/root/flag.txt', 'root', 'root')
        self.flags['192.168.199.4'] = setup_flag(self.ansible_runner, '192.168.199.4', '/home/ubuntu/flag.txt', 'ubuntu', 'admin')

        # Install priv escelation
        params = {'host': '192.168.199.4'}
        r = self.ansible_runner.run_playbook('vulnerabilities/writeablePasswd.yml', playbook_params=params)

        # Enable ssh passlogin
        params = {'host': '192.168.199.4'}
        r = self.ansible_runner.run_playbook('vulnerabilities/sshEnablePasswordLogin.yml', playbook_params=params)
