import argparse
from AnsibleRunner import AnsibleRunner
from os import getcwd, chmod
from os.path import exists
import stat

"""
Execution command: python agent_install.py -t <Target IP address> -c <Caldera IP address> -s <Path to SSH private key>
To execute in background: agent_install.py -t <Target IP address> -c <Caldera IP address> -s <Path to SSH private key> &> /dev/null &
"""
def install(target_ip, server_ip, ssh_key, user_name, ansible_dir = 'ansible/caldera'):
    # Confirm if installer script is present
    if not exists('install.sh'):
        print("Installer script not present! Exiting...")
        exit(1)

    # Get location of installer script
    installer_path = getcwd() + "/install.sh"

    # Begin Ansible Runner
    ansible_runner = AnsibleRunner(ssh_key, target_ip, ansible_dir)

    remote_cmd = "~/install.sh"
    params = {'remote_path': remote_cmd, 'local_path': installer_path, 'caldera_ip': server_ip, 'username': user_name}
    r = ansible_runner.run_playbook('install.yml', playbook_params=params)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--target_ip', help = 'IP address of target machine', required = True)
    parser.add_argument('-s', '--ssh_key', help = 'The path to your openstack ssh key', required = True)
    parser.add_argument('-c', '--caldera_ip', help = 'IP address of caldera machine', required=True)
    parser.add_argument('-u', '--username', help = 'Username of target machine')
    args = parser.parse_args()
    username = "ubuntu"
    if args.username:
        username = args.username
    install(args.target_ip, args.caldera_ip, args.ssh_key, username)

