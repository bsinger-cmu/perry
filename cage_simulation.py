import argparse

from AnsibleRunner import AnsibleRunner
from environment import CageEnvironment

import openstack

import time

from attacker import Attacker
from defender import WaitAndSpotDefender

from openstack_helper_functions.server_helpers import shutdown_server_by_name

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

def main(ssh_key_path, ansible_dir, caldera_ip, caldera_api_key):
    # Setup connection to openstack
    conn = initialize()
    manage_server, manage_ip = find_manage_server(conn)

    # Initialize ansible
    ansible_runner = AnsibleRunner(ssh_key_path, manage_ip, ansible_dir)

    # Setup cage environment
    # TODO Brian: In the future we probably want to have this redeploy the entire terraform environment
    cage_env = CageEnvironment(ansible_runner, conn)
    cage_env.setup()

    # # Setup initial attacker
    # params = {'host': '192.168.199.3', 'user': 'ubuntu', 'caldera_ip': caldera_ip}
    # r = ansible_runner.run_playbook('caldera/install_attacker.yml', playbook_params=params)
    
    # # Setup attacker
    # attacker = Attacker(caldera_api_key)

    # # Setup initial defender
    # defender = WaitAndSpotDefender(ansible_runner, conn)
    # defender.start()

    # # Start attacker
    # attacker.start_operation()

    # # shutdown_server_by_name(conn, 'sub1_host1')
    # print('Defender loop starting!')
    # try:
    #     while True:
    #         defender.run()
    #         time.sleep(.1)

    #         # Use Caldera API to start an operation
    #         attacker.start_operation()
    
    # except KeyboardInterrupt:
    #     pass

    ### EXAMPLES ###
    # params = {'host': '192.168.200.3', 'user': 'ubuntu', 'ssh_key_path': '../../attacker.pub'}
    # r = ansible_runner.run_playbook('addSSHKey.yml', playbook_params=params)

    # params = {'host': '192.168.199.3', 'user': 'ubuntu'}
    # r = ansible_runner.run_playbook('vulnerabilities/weakUserPassword.yml', playbook_params=params)

    # params = {'host': '192.168.199.3'}
    # r = ansible_runner.run_playbook('vulnerabilities/writeablePasswdSudoers.yml', playbook_params=params)

    # r = ansible_runner.run_playbook('common/testPlaybook.yml')

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--ssh_key_path', help='The path to your openstack ssh key')
    parser.add_argument('-c', '--caldera_ip', help = 'IP address of caldera machine', required=True)
    parser.add_argument('-a', '--caldera_api_key', help = 'API key of caldera', required=True)
    # TODO dymnamic inventory
    # parser.add_argument('-i', '--inventory', help='The path the ansible inventory')
    args = parser.parse_args()

    main(args.ssh_key_path, './ansible/', args.caldera_ip, args.caldera_api_key)
