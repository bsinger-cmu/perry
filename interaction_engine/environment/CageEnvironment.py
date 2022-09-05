from os import chmod
from Crypto.PublicKey import RSA

class CageEnvironment:
    def __init__(self, ansible_runner, openstack_conn):
        self.ansible_runner = ansible_runner
        self.openstack_conn = openstack_conn
        self.ssh_key_path = './environment/ssh_keys/'

    def setup(self, attacker_initial_access):
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
        params = {'host': '192.168.200.3', 'user': 'ubuntu', 'ssh_key_path': '../../environment/ssh_keys/attacker.pub'}
        r = self.ansible_runner.run_playbook('addSSHKey.yml', playbook_params=params)

