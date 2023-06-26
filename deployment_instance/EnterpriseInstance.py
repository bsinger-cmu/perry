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


        # # ActiveDir:    192.168.200.3      <-- Samba RCE vulnerability (or - currently - netcat reverse shell) -- shell command
        # # CEO:          192.168.200.4 FLAG <-- SSH password login, passwd writeable -- shell commands
        # # Finance:      192.168.200.5 FLAG <-- VSFTP Backdoor vulnerability -- script
        # $ HR:           192.168.200.6
        # ! Intern:       192.168.200.7      <-- infected with attacker (SSH password login)
        # # Database:     192.168.201.3 FLAG <-- SSH password login, weak user password (or netcat reverse shell) -- script + shell command
        
        self.orchestrator.deployment.check_host_liveness('192.168.200.3')
        time.sleep(3)

        # Install users on all hosts
        self.orchestrator.common.create_user('192.168.200.3', 'activedir', 'ubuntu')
        self.orchestrator.common.create_user('192.168.200.4', 'ceo', 'ubuntu')
        self.orchestrator.common.create_user('192.168.200.5', 'finance', 'ubuntu')
        self.orchestrator.common.create_user('192.168.200.6', 'hr', 'ubuntu')
        self.orchestrator.common.create_user('192.168.200.7', 'intern', 'ubuntu')
        self.orchestrator.common.create_user('192.168.201.3', 'database', 'ubuntu')
        
        # Add vulnerabilities to hosts
        # Active Directory
        self.orchestrator.vulns.add_netcatShell('192.168.200.3')
        # CEO
        self.orchestrator.vulns.add_sshEnablePasswordLogin('192.168.200.4')
        self.orchestrator.vulns.add_writeablePassword('192.168.200.4')
        # Finance
        self.orchestrator.vulns.add_vsftpdBackdoor('192.168.200.5')
        # Intern
        self.orchestrator.vulns.add_sshEnablePasswordLogin('192.168.200.7')
        # Database
        self.orchestrator.vulns.add_weakUserPassword('192.168.201.3', 'database')
        self.orchestrator.vulns.add_sshEnablePasswordLogin('192.168.201.3')
        self.orchestrator.vulns.add_netcatShell('192.168.201.3')

        # Setup attacker on intern machine
        self.orchestrator.attacker.install_attacker('192.168.200.7', 'intern', self.caldera_ip)

        # Setup flags
        self.flags['192.168.200.4'] = self.orchestrator.goals.setup_flag('192.168.200.4', '/home/ceo/flag.txt', 'ceo', 'root')
        self.flags['192.168.200.5'] = self.orchestrator.goals.setup_flag('192.168.200.5', '/home/finance/flag.txt', 'finance', 'root')
        self.flags['192.168.201.3'] = self.orchestrator.goals.setup_flag('192.168.201.3', '/home/database/flag.txt', 'database', 'root')

