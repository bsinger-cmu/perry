import argparse

from AnsibleRunner import AnsibleRunner
from deployment_instance import SimpleInstanceV1

import openstack

import time

from attacker import Attacker
from defender import WaitAndSpotDefender

from rich import print
from os import path
import yaml
from elasticsearch import Elasticsearch


def initialize():
    # Initialize connection
    conn = openstack.connect(cloud='default')
    return conn

def main(config):
    # Setup connection to openstack
    conn = initialize()

    # Setup connection to elasticsearch
    elasticsearch_server = f"https://localhost:{config['elasticsearch']['port']}"
    elasticsearch_api_key = config['elasticsearch']['api_key']

    elasticsearch_conn = Elasticsearch(
        elasticsearch_server,
        basic_auth=("elastic", elasticsearch_api_key),
        verify_certs=False
    )

    # Initialize ansible
    ssh_key_path = config['ssh_key_path']
    ansible_dir = './ansible/'
    ansible_runner = AnsibleRunner(ssh_key_path, None, ansible_dir)

    # # Deploy deployment instance
    # simple_instance = SimpleInstanceV1(ansible_runner, conn)
    # simple_instance.setup()

    # # Setup initial attacker
    # caldera_ip = f"{config['external_ip']}:{config['caldera']['port']}"
    # params = {'host': '192.168.199.3', 'user': 'ubuntu', 'caldera_ip': caldera_ip}
    # r = ansible_runner.run_playbook('caldera/install_attacker.yml', playbook_params=params)
    
    # # Setup attacker
    # caldera_api_key = config['caldera']['api_key']
    # attacker = Attacker(caldera_api_key)

    # Setup initial defender
    defender = WaitAndSpotDefender(ansible_runner, conn, elasticsearch_conn, config['external_ip'], config['elasticsearch']['port'], config['elasticsearch']['api_key'])
    defender.start()

    # Start attacker
    # attacker.start_operation()

    # shutdown_server_by_name(conn, 'sub1_host1')
    print('Defender loop starting!')
    try:
        while True:
            defender.run()
            time.sleep(.5)

            # # Use Caldera API to start an operation
            # attacker.start_operation()
    
    except KeyboardInterrupt:
        pass

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Name of configuration file')
    args = parser.parse_args()

    # open yml config file
    with open(path.join('config', args.config), 'r') as f:
        config = yaml.safe_load(f)

    main(config)
