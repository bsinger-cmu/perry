from os import chmod
from Crypto.PublicKey import RSA
from environment.Environment import Environment
from environment.SetupFlag import setup_flag


class CageEnvironment(Environment):
    def __init__(self, ansible_runner, openstack_conn):
        super().__init__(ansible_runner, openstack_conn)

    def setup(self):
        # Install sshpass for exploit
        params = {'host': '192.168.199.3', 'package': 'sshpass'}
        r = self.ansible_runner.run_playbook('common/installPackage.yml', playbook_params=params)

        # Setup user
        params = {'host': '192.168.200.3', 'user': 'ubuntu', 'password': 'ubuntu'}
        r = self.ansible_runner.run_playbook('common/createUser.yml', playbook_params=params)

        # Setup flag
        flag = setup_flag(self.ansible_runner, '192.168.200.3', '/home/ubuntu/flag.txt', 'root', 'root')

        # Install priv escelation
        params = {'host': '192.168.200.3'}
        r = self.ansible_runner.run_playbook('vulnerabilities/writeablePasswd.yml', playbook_params=params)

        # Enable ssh passlogin
        params = {'host': '192.168.200.3'}
        r = self.ansible_runner.run_playbook('vulnerabilities/sshEnablePasswordLogin.yml', playbook_params=params)

        self.flags[flag] = 1
