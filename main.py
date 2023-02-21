import argparse

from AnsibleRunner import AnsibleRunner
from deployment_instance import SimpleInstanceV1

import openstack

import time

from attacker import Attacker
from defender import WaitAndSpotDefender

from rich import print


def initialize():
    # Initialize connection
    conn = openstack.connect(cloud='default')
    return conn

def main(ssh_key_path, ansible_dir, caldera_ip, caldera_api_key):
    # Setup connection to openstack
    conn = initialize()

    # Initialize ansible
    ansible_runner = AnsibleRunner(ssh_key_path, None, ansible_dir)

    # Deploy deployment instance
    simple_instance = SimpleInstanceV1(ansible_runner, conn)
    simple_instance.setup()

    # Setup initial attacker
    params = {'host': '192.168.199.3', 'user': 'ubuntu', 'caldera_ip': caldera_ip}
    r = ansible_runner.run_playbook('caldera/install_attacker.yml', playbook_params=params)
    
    # Setup attacker
    attacker = Attacker(caldera_api_key)

    # Setup initial defender
    defender = WaitAndSpotDefender(ansible_runner, conn)
    defender.start()

    # Start attacker
    attacker.start_operation()

    # shutdown_server_by_name(conn, 'sub1_host1')
    print('Defender loop starting!')
    try:
        while True:
            defender.run()
            time.sleep(.1)

            # Use Caldera API to start an operation
            attacker.start_operation()
    
    except KeyboardInterrupt:
        pass

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--ssh_key_path', help='The path to your openstack ssh key')
    parser.add_argument('-c', '--caldera_ip', help = 'IP address of caldera machine', required=True)
    parser.add_argument('-a', '--caldera_api_key', help = 'API key of caldera', required=True)
    # TODO dymnamic inventory
    # parser.add_argument('-i', '--inventory', help='The path the ansible inventory')
    args = parser.parse_args()

    main(args.ssh_key_path, './ansible/', args.caldera_ip, args.caldera_api_key)
