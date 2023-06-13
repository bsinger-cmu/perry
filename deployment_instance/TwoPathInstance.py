from os import chmod
from Crypto.PublicKey import RSA
from deployment_instance import DeploymentInstance
from deployment_instance.SetupFlag import setup_flag
from deployment_instance.topology_orchestrator import deploy_network, destroy_network
import random
import time

                
class TwoPathInstance(DeploymentInstance):

    def setup(self, already_deployed=False):
        # Setup topology
        if not already_deployed:
            destroy_network('two_path_network')
            deploy_network('two_path_network')
            time.sleep(5)

        # Update management ip for new network
        # TODO have management server be fixed, and only deploy instance servers
        self.find_management_server()

        params = {'host': '192.168.200.3'}
        r = self.ansible_runner.run_playbook('deployment_instance/check_if_host_up.yml', playbook_params=params)
        time.sleep(3)

        # Install ubuntu users on all servers
        params = {'host': '192.168.200.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        params = {'host': '192.168.201.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        params = {'host': '192.168.202.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        params = {'host': '192.168.203.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)

        # # Install SysFlow
        # params = {'host': '192.168.200.3'}
        # r = self.ansible_runner.run_playbook('defender/sysflow/install_sysflow.yml', playbook_params=params)
        # params = {'host': '192.168.201.3'}
        # r = self.ansible_runner.run_playbook('defender/sysflow/install_sysflow.yml', playbook_params=params)
        # params = {'host': '192.168.202.3'}
        # r = self.ansible_runner.run_playbook('defender/sysflow/install_sysflow.yml', playbook_params=params)
        # params = {'host': '192.168.203.3'}
        # r = self.ansible_runner.run_playbook('defender/sysflow/install_sysflow.yml', playbook_params=params)

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

        # print('Sleeping for 10 min of baseline data')
        # time.sleep(600)
        
        # Setup initial attacker
        params = {'host': '192.168.200.3', 'user': 'ubuntu', 'caldera_ip': self.caldera_ip}
        self.ansible_runner.run_playbook('caldera/install_attacker.yml', playbook_params=params)

        # Setup flag
        self.flags['192.168.203.3'] = setup_flag(self.ansible_runner, '192.168.203.3', '/home/ubuntu/flag.txt', 'ubuntu', 'root')
