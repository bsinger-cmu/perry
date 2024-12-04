from enum import Enum
import random

from .Defender import Defender
from .capabilities import StartHoneyService, ShutdownServer, DeployDecoy
from .strategy.setup.RandomPlacement import randomly_place_deception


class EnterpriseRandomDefender(Defender):
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

        # self.telemetry_analysis = SimpleTelemetryAnalysis(self.elasticsearch_conn)

    def start(self):
        print("Starting EnterpriseSimpleDefender")
        self.deploy_deception()
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

    def deploy_deception(self):
        # Deploy deception randomly
        actions = randomly_place_deception(self.arsenal, self.hosts, self.networks)
        self.orchestrator.run(actions)
        return

    def run(self):
        super().run()
        # new_events = self.telemetry_analysis.process_low_level_events()
        # actions_to_execute = []

        # for event in new_events:
        #     attacker_ip = event.attacker_ip
        #     print(f'Attacker found on {attacker_ip}, turning off host.')
        #     actions_to_execute.append(ShutdownServer(attacker_ip))

        # self.orchestrator.run(actions_to_execute)

        return
