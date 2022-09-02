import ansible_runner

from agents.SimpleAttacker import SimpleAttacker
from environment.Environment import Environment
from environment.Host import Host

from openstack_helper_functions.server_helpers import find_server_by_name

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

def main():
    # Setup connection to openstack
    conn = initialize()
    manage_server, manage_ip = find_manage_server(conn)

    # Setup attacker
    attacker = SimpleAttacker()

    # Setup environment
    env = Environment(conn)
    env.attackers.append(attacker)
    env.attacker_hosts[attacker] = []
    
    # Create host for attacker to have initial access to
    compromised_host = find_server_by_name(conn, 'sub1_host1')
    # Find host by name
    env.attacker_hosts[attacker].append(compromised_host)

    attacker.step(env)

    

if __name__ == "__main__":
    main()
