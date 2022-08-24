import ansible_runner
import openstack
import argparse
from rich import print

def initialize():
    # Initialize connection
    conn = openstack.connect(cloud='default')
    return conn

public_ip = '10.20.20'
def find_manage_server(conn):
    for server in conn.compute.servers():
        for network, network_attrs in server.addresses.items():
            ip_addresses = [x['addr'] for x in network_attrs]
            for ip in ip_addresses:
                if public_ip in ip:
                    return server, ip

def run_bash_command(ansible_def_vars, data_dir, command):
    print(data_dir)
    print(command)
    ansible_def_vars['command'] = command
    r = ansible_runner.run(extravars=ansible_def_vars, private_data_dir=data_dir, playbook='generic_commands.yml')
    print(r)
    output = []

    for event in r.events:
        if 'event_data' in event:
            if 'res' in event['event_data']:
                if 'cmd' in event['event_data']['res'] and len(event['event_data']['res']['cmd']) > 0:
                    if event['event_data']['res']['cmd'][0] == 'pwd':
                        output.append(event['event_data']['res']['stdout_lines'])
    
    return output

def main(args):
    conn = initialize()
    manage_server, manage_ip = find_manage_server(conn)
    ansible_data_dir = '../ansible/cage/'
    ansible_vars_default = {'manage_ip': manage_ip, 'ssh_key_path': args.ssh_key_path}
    output = run_bash_command(ansible_vars_default, ansible_data_dir, 'pwd')
    print(output)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ssh_key_path', help='The path to your openstack ssh key')
    args = parser.parse_args()

    main(args)
