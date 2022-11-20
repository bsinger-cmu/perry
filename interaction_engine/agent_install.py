import argparse
from AnsibleRunner import AnsibleRunner
from os import getcwd, chmod
from os.path import exists
import cage_simulation
import stat

"""
Execution command: python agent_install.py -t <Target IP address> -c <Caldera IP address> -s <Path to SSH private key>
"""
def install(target_ip, server_ip, ssh_key, mode, user_name, ansible_dir = 'ansible'):
    install_path = f"{ansible_dir}/caldera"
    # Confirm if installer script is present
    if not exists(install_path):
        print("Installer script not present! Exiting...")
        exit(1)

    #Setup connection to openstack
    conn = cage_simulation.initialize()
    _, manage_ip = cage_simulation.find_manage_server(conn)

    # Initialize ansible
    ansible_runner = AnsibleRunner(ssh_key, manage_ip, ansible_dir)

    params = {'host': target_ip, 'caldera_ip': server_ip, 'user': user_name}
    if mode == 'red':
        r = ansible_runner.run_playbook('caldera/install_attacker.yml', playbook_params=params)
    else:
        r = ansible_runner.run_playbook('caldera/install_defender.yml', playbook_params=params)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--target_ip', help = 'IP address of target machine', required = True)
    parser.add_argument('-s', '--ssh_key', help = 'The path to your openstack ssh key', required = True)
    parser.add_argument('-c', '--caldera_ip', help = 'IP address of caldera machine', required = True)
    parser.add_argument('-u', '--username', help = 'Username of target machine')
    parser.add_argument('-m', '--mode', help = 'Agent mode (red/blue)', required = True)
    args = parser.parse_args()
    username = "ubuntu"
    if args.username:
        username = args.username
    if args.mode != 'red' and args.mode != 'blue':
        print("Incorrect mode provided. Defaulting to red...")
        args.mode = 'red'

    install(args.target_ip, args.caldera_ip, args.ssh_key, args.mode, username)

