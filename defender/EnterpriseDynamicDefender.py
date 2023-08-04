from enum import Enum

from .Defender import Defender
from .capabilities import StartHoneyService, ShutdownServer, RestoreServer, DeployDecoy
from .telemetry import SimpleTelemetryAnalysis

class EnterpriseDynamicDefender(Defender):

    def __init__(self, ansible_runner, openstack_conn, elasticsearch_conn, external_ip, elasticsearch_port, elasticsearch_api_key, arsenal):
        super().__init__(ansible_runner, openstack_conn, elasticsearch_conn, external_ip, elasticsearch_port, elasticsearch_api_key, arsenal)
        
        self.telemetry_analysis = SimpleTelemetryAnalysis(self.elasticsearch_conn)
        self.metrics = {
            'total_host_restores': 0,
            'count_host_restores': {},
            'total_decoy_deployments': 0,
        }

        self.decoy_info = {'network': 'datacenter_network', 'server': 'decoy_', 'sec_group': 'datacenter'}
        self.decoys = 0

    def start(self):
        print("Starting EnterpriseDynamicDefender")
        self.deploy_telemetry()
        return
    
    def deploy_telemetry(self):
        # Deploy honey service
        actions = [
            StartHoneyService('192.168.200.3'),
            StartHoneyService('192.168.200.5'),
            StartHoneyService('192.168.200.6'),
            StartHoneyService('192.168.201.3'),
            # StartHoneyService('192.168.201.3', port="4444", service="telnet"),
            # StartHoneyService('192.168.201.3', port="21", service="ftp"),
        ]
        
        self.orchestrator.run(actions)
        return
    
    def run(self):
        new_events = self.telemetry_analysis.process_low_level_events()
        hosts_to_restore = []
        decoys_to_deploy = []

        ips_to_shutdown = set()
        deploy_decoy = False

        for event in new_events:
            attacker_ip = event.attacker_ip
            print(f'Attacker found on {attacker_ip}, preparing to restore host.')
            # actions_to_execute.append(ShutdownServer(attacker_ip))
            ips_to_shutdown.add(attacker_ip)
            deploy_decoy =  True

        for ip in ips_to_shutdown:
            hosts_to_restore.append(RestoreServer(ip))
            self.metrics['total_host_restores'] += 1
            print(f"Restoring host {ip}")
            if ip in self.metrics['count_host_restores']:
                self.metrics['count_host_restores'][ip] += 1
            else:
                self.metrics['count_host_restores'][ip] = 1

        self.orchestrator.run(hosts_to_restore)

        if deploy_decoy and self.decoys < 3:
            self.decoys += 1
            self.decoy_info['server'] = "decoy_" + str(self.decoys)
            self.metrics['total_decoy_deployments'] += 1

            print(f"Deploying decoy {self.decoy_info['server']}")
            decoys_to_deploy.append(DeployDecoy(sec_group=self.decoy_info['sec_group'], 
                                                network=self.decoy_info['network'], 
                                                server=self.decoy_info['server']))

        self.orchestrator.run(decoys_to_deploy)

        return