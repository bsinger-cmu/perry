from os import chmod
from Crypto.PublicKey import RSA
from environment.Environment import Environment
from environment.SetupFlag import setup_flag


class CageEnvironment(Environment):
    def __init__(self, ansible_runner, openstack_conn):
        super().__init__(ansible_runner, openstack_conn)


    def setup_ssh_key(self, host):
        # Generate attacker key
        attacker_key = RSA.generate(2048)
        attacker_private_key_name = self.ssh_key_path + 'attacker.pem'
        attacker_public_key_name = self.ssh_key_path + 'attacker.pub'

        # Private key
        with open(attacker_private_key_name, 'wb') as content_file:
            chmod(attacker_private_key_name, 0o0600)
            content_file.write(attacker_key.exportKey('PEM'))
        pubkey = attacker_key.publickey()
        with open(attacker_public_key_name, 'wb') as content_file:
            content_file.write(pubkey.exportKey('OpenSSH'))

        # Add ssh key to the host the attacker has initial access to
        # TODO fix this ssh path issue
        params = {'host': host, 'user': 'ubuntu', 'ssh_key_path': '../../environment/ssh_keys/attacker.pub'}
        r = self.ansible_runner.run_playbook('addSSHKey.yml', playbook_params=params)

    def setup(self):
        # self.setup_ssh_key('192.168.200.3')

        # Setup flag
        flag = setup_flag(self.ansible_runner, '192.168.199.3', '/root/flag.txt', 'root', 'root')
        self.flags[flag] = 1
