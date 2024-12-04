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
            'count_decoy_deployments': {},
        }

        self.decoy_datacenter = {'network': 'datacenter_network', 
                                 'sec_group': 'datacenter'}
        self.decoy_company = {'network': 'company_network', 
                              'sec_group': 'company'}
        self.decoys = 0

    def start(self):
        print("Starting EnterpriseDynamicDefender")
        self.deploy_telemetry()
        return
    
    def deploy_telemetry(self):
        # Deploy honey service
        actions = [
            StartHoneyService('192.168.200.3'),
            StartHoneyService('192.168.200.4'),
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
        attacker_ip = None

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

        if deploy_decoy and self.decoys < 6:
            decoy = self.decoy_datacenter

            # This method is smarter. Experiment folder: experiment_3_v2
            if attacker_ip and attacker_ip.startswith('192.168.200'):
                decoy = self.decoy_company
            # Old Method. Experiment folder: experiment_3, experiment_3_test
            # if self.decoys % 2 == 0:
            #     decoy = self.decoy_company
            
            self.decoys += 1
            decoy_name = "decoy_" + str(self.decoys)
            
            self.metrics['total_decoy_deployments'] += 1

            if decoy['network'] in self.metrics['count_decoy_deployments']:
                self.metrics['count_decoy_deployments'][decoy['network']] += 1
            else:
                self.metrics['count_decoy_deployments'][decoy['network']] = 1

            print(f"Deploying decoy {decoy_name} on network {decoy['network']}")
            decoys_to_deploy.append(DeployDecoy(sec_group=decoy['sec_group'], 
                                                network=decoy['network'], 
                                                server=decoy_name))

        self.orchestrator.run(decoys_to_deploy)

        return