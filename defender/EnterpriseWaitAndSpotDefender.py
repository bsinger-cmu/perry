from enum import Enum

from .Defender import Defender
from .capabilities import StartHoneyService, ShutdownServer, RestoreServer, DeployDecoy
from .telemetry import SimpleTelemetryAnalysis

from .strategy.setup.RandomPlacement import randomly_place_deception


class EnterpriseWaitAndSpotDefender(Defender):
    def __init__(
        self,
        ansible_runner,
        openstack_conn,
        elasticsearch_conn,
        external_ip,
        elasticsearch_port,
        elasticsearch_api_key,
        arsenal,
    ):
        super().__init__(
            ansible_runner,
            openstack_conn,
            elasticsearch_conn,
            external_ip,
            elasticsearch_port,
            elasticsearch_api_key,
            arsenal,
        )

        self.telemetry_analysis = SimpleTelemetryAnalysis(self.elasticsearch_conn)
        self.metrics = {
            "total_host_restores": 0,
            "count_host_restores": {},
        }

    def start(self):
        print("Starting EnterpriseWaitAndSpotDefender")
        self.deploy_telemetry()
        return

    hosts = [
        "192.168.200.3",
        "192.168.200.4",
        "192.168.200.5",
        "192.168.200.6",
        "192.168.200.7",
        "192.168.201.3",
    ]

    networks = [
        {"network": "datacenter_network", "sec_group": "datacenter"},
        {"network": "company_network", "sec_group": "company"},
    ]

    def deploy_telemetry(self):
        # Deploy deception randomly
        actions = randomly_place_deception(self.arsenal, self.hosts, self.networks)
        self.orchestrator.run(actions)

    def run(self):
        new_events = self.telemetry_analysis.process_low_level_events()
        actions_to_execute = []
        ips_to_shutdown = set()

        for event in new_events:
            attacker_ip = event.attacker_ip
            # actions_to_execute.append(ShutdownServer(attacker_ip))
            ips_to_shutdown.add(attacker_ip)
            print(f"new event found on {attacker_ip}")

        for ip in ips_to_shutdown:
            print(f"Attacker found on {ip}, restoring host...")
            actions_to_execute.append(RestoreServer(ip))
            self.metrics["total_host_restores"] += 1
            print(f"Restoring host {ip}")
            if ip in self.metrics["count_host_restores"]:
                self.metrics["count_host_restores"][ip] += 1
            else:
                self.metrics["count_host_restores"][ip] = 1

        self.orchestrator.run(actions_to_execute)

        return
