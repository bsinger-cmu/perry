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
            destroy_network('enterprise_network')
            deploy_network('enterprise_network')
            time.sleep(5)

        # Update management ip for new network
        # TODO (copied from TwoPathInstance.py) have management server be fixed, and only deploy instance servers
        self.find_management_server()


        # # ActiveDir:    192.168.200.3      <-- Samba RCE vulnerability
        # # CEO:          192.168.200.4 FLAG <-- SSH login, sudoers writeable
        # # Finance:      192.168.200.5 FLAG <-- VSTP Backdoor vulnerability
        # $ HR:           192.168.200.6
        # ! Intern:       192.168.200.7      <-- infected with attacker (SSH login)
        # # Database:     192.168.201.3 FLAG <-- SSH login, weak user password
        
        self.orchestrator.deployment.check_host_liveness('192.168.200.3')
        time.sleep(3)

        # Install users on all hosts
        self.orchestrator.common.create_user('192.168.200.3', 'activedir', 'ubuntu')
        self.orchestrator.common.create_user('192.168.200.4', 'ceo', 'ubuntu')
        self.orchestrator.common.create_user('192.168.200.5', 'finance', 'ubuntu')
        self.orchestrator.common.create_user('192.168.200.6', 'hr', 'ubuntu')
        self.orchestrator.common.create_user('192.168.200.7', 'intern', 'ubuntu')
        self.orchestrator.common.create_user('192.168.201.3', 'database', 'ubuntu')

        #Add Samba AD DC, create users/groups, and configure host machines to join AD
        self.orchestrator.enterprise.samba_AD('192.168.200.3', 'ENTERPRISE', 'DECEPTION.LCL', 'nBMat41l0cY&')
        self.orchestrator.enterprise.add_Groups('192.168.200.3')
        self.orchestrator.enterprise.add_Users('192.168.200.3', 'deployment_instance/user_details.yml')
        self.orchestrator.enterprise.join_AD('192.168.200.4')
        self.orchestrator.enterprise.join_AD('192.168.200.5')
        self.orchestrator.enterprise.join_AD('192.168.200.6')
        self.orchestrator.enterprise.join_AD('192.168.200.7')
        self.orchestrator.enterprise.join_AD('192.168.201.3')
        
        # Add vulnerabilities to hosts
        self.orchestrator.vulns.add_sshEnablePasswordLogin('192.168.200.4')
        self.orchestrator.vulns.add_writeableSudoers('192.168.200.4')
        # self.orchestrator.vulns.add_vsftpdBackdoor('192.168.200.5')
        self.orchestrator.vulns.add_sshEnablePasswordLogin('192.168.200.5')
        self.orchestrator.vulns.add_weakUserPassword('192.168.201.3', 'database')
        self.orchestrator.vulns.add_sshEnablePasswordLogin('192.168.201.3')

        # Setup initial attacker on intern machine
        self.orchestrator.attacker.install_attacker('192.168.200.7', 'intern', self.caldera_ip)
        self.orchestrator.vulns.add_sshEnablePasswordLogin('192.168.200.7')


        # Setup flags
        self.flags['192.168.200.4'] = self.orchestrator.goals.setup_flag('192.168.200.4', '/home/ceo/flag.txt', 'ceo', 'root')
        self.flags['192.168.200.5'] = self.orchestrator.goals.setup_flag('192.168.200.5', '/home/finance/flag.txt', 'finance', 'root')
        self.flags['192.168.201.3'] = self.orchestrator.goals.setup_flag('192.168.201.3', '/home/database/flag.txt', 'database', 'root')

