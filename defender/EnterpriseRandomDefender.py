from enum import Enum
import random

from .Defender import Defender
from .capabilities import StartHoneyService, ShutdownServer, DeployDecoy
from .telemetry import SimpleTelemetryAnalysis


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
        num_honeyservice = self.arsenal.storage["HoneyService"]
        num_decoys = self.arsenal.storage["DeployDecoy"]

        # Randomly deploy honey service hosts
        random.shuffle(self.hosts)
        actions = []
        for i in range(0, num_honeyservice):
            actions.append(StartHoneyService(self.hosts[i]))

        # Randomly deploy decoys on networks
        for i in range(0, num_decoys):
            random.shuffle(self.networks)
            network_to_deploy = self.networks[0]
            decoy_name = f"decoy_{i}"

            decoy_action = DeployDecoy(
                sec_group=network_to_deploy["sec_group"],
                network=network_to_deploy["network"],
                server=decoy_name,
            )

            actions.append(decoy_action)

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
