import argparse
import importlib
from os import path
import openstack

import yaml

from AnsibleRunner import AnsibleRunner
# deployment_instance_module = importlib.import_module('deployment_instance')
from deployment_instance import DeploymentInstance

class ModifyInstance():
    def __init__(self):
        self.openstack_conn = openstack.connect(cloud='default')
        pass
    
    def test(self, config, scenario):
        ssh_key_path = config['ssh_key_path']
        ansible_dir = './ansible/'
        ansible_runner = AnsibleRunner(ssh_key_path, None, ansible_dir)
        
        host = '192.168.200.5'
        # deployment_instance_ = getattr(deployment_instance_module, scenario['deployment_instance'])
        self.deployment_instance = DeploymentInstance(ansible_runner, self.openstack_conn, config['external_ip'])
        # self.deployment_instance.orchestrator.common.reboot(host)
        # self.deployment_instance.orchestrator.vulns.add_sshEnablePasswordLogin(host)
        self.deployment_instance.orchestrator.vulns.add_vsftpdBackdoor(host)
        self.deployment_instance.orchestrator.vulns.run_vsftpdBackdoor(host)
        # self.deployment_instance.orchestrator.vulns.add_netcatShell(host)
        # self.deployment_instance.orchestrator.common.install_package(host, "ncat")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Name of configuration file')
    parser.add_argument('-s', '--scenario', help='Name of scenario file')
    args = parser.parse_args()

    # open yml config file
    with open(path.join('config', args.config), 'r') as f:
        config = yaml.safe_load(f)

    # open yml config file
    with open(path.join('scenarios', args.scenario), 'r') as f:
        scenario = yaml.safe_load(f)
    mod = ModifyInstance()
    mod.test(config, scenario)
