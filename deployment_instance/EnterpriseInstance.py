from os import chmod
from Crypto.PublicKey import RSA
from deployment_instance import DeploymentInstance
from deployment_instance.SetupFlag import setup_flag
from deployment_instance.topology_orchestrator import deploy_network, destroy_network
import random
import time

class EnterpriseInstance(DeploymentInstance):
    def setup(self, already_deployed=False):
        # Setup topology
        if not already_deployed:
            print('Redeploying network...')
            destroy_network('enterprise_network')
            deploy_network('enterprise_network')
            time.sleep(7)
            print('Network redeployed')

        # Update management ip for new network
        # TODO (copied from TwoPathInstance.py) have management server be fixed, and only deploy instance servers
        self.find_management_server()


        # ActiveDir:    192.168.200.3  <-- Samba RCE vulnerability
        # CEO:          192.168.200.4 FLAG <-- Weak (sudo) user credentials vulnerability
        # Finance:      192.168.200.5 FLAG <-- VSTP Backdoor vulnerability
        # HR:           192.168.200.6
        # Intern:       192.168.200.7  <-- infected with attacker
        # Database:     192.168.201.3 FLAG <-- Netcat Shell vulnerability
        
        params = {'host': '192.168.200.3'}
        r = self.ansible_runner.run_playbook('deployment_instance/check_if_host_up.yml', playbook_params=params)
        time.sleep(3)

        # Install users on all hosts
        params = {'host': '192.168.200.3', 'user': 'activedir', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        
        params = {'host': '192.168.200.4', 'user': 'ceo', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        
        params = {'host': '192.168.200.5', 'user': 'finance', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        
        params = {'host': '192.168.200.6', 'user': 'humanresources', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        
        params = {'host': '192.168.200.7', 'user': 'intern', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)
        
        params = {'host': '192.168.201.3', 'user': 'database', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)

        # TODO: Add vulnerabilities to hosts
        self.vuln_orch.add_sshEnablePasswordLogin('192.168.200.3') ## TEMP VULN
        self.vuln_orch.add_sshEnablePasswordLogin('192.168.200.4') ## TEMP VULN
        self.vuln_orch.add_sshEnablePasswordLogin('192.168.201.3') ## TEMP VULN

        # Setup initial attacker on intern machine
        params = {'host': '192.168.200.7', 'user': 'intern', 'caldera_ip': self.caldera_ip}
        r = self.ansible_runner.run_playbook('candera/setup_attacker.yml', playbook_params=params)


        # Setup flags
        self.flags['192.168.200.4'] = setup_flag(self.ansible_runner, '192.168.200.1', '/home/ceo/flag.txt', 'ceo', 'root')
        self.flags['192.168.200.5'] = setup_flag(self.ansible_runner, '192.168.200.2', '/home/finance/flag.txt', 'finance', 'root')
        self.flags['192.168.201.3'] = setup_flag(self.ansible_runner, '192.168.201.0', '/home/database/flag.txt', 'database', 'root')