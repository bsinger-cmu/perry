import argparse

from AnsibleRunner import AnsibleRunner

import openstack

from rich import print


def initialize():
    # Initialize connection
    conn = openstack.connect(cloud='default')
    return conn


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

def main(ssh_key_path, ansible_dir):
    # Setup connection to openstack
    conn = initialize()
    manage_server, manage_ip = find_manage_server(conn)

    # Initialize ansible
    ansible_runner = AnsibleRunner(ssh_key_path, manage_ip, ansible_dir)

    params = {'host': '192.168.200.3', 'user': 'ubuntu', 'ssh_key_path': '../../attacker.pub'}
    r = ansible_runner.run_playbook('addSSHKey.yml', playbook_params=params)
    #r = ansible_runner.run_playbook('testPlaybook.yml')
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--ssh_key_path', help='The path to your openstack ssh key')
    parser.add_argument('-a', '--ansible_dir', help='The path the ansible directory')
    args = parser.parse_args()

    main(args.ssh_key_path, args.ansible_dir)
