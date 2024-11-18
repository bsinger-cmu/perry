from deployment_instance.network import Host
from defender.capabilities import (
    DeployDecoy,
    AddHoneyCredentials,
    RestoreServer,
)

from defender.telemetry.events import (
    DecoyHostInteraction,
    DecoyCredentialUsed,
    SSHEvent,
)
from . import Strategy

from utility.logging import log_event


class ReactiveLayered(Strategy):
    # Run actions before the scenario starts
    def initialize(self):
        log_event("ReactiveLayered", "Initializing ReactiveLayered strategy")
        num_decoys = self.arsenal.storage["DeployDecoy"]
        num_honeycreds = self.arsenal.storage["HoneyCredentials"]

        # Get max restores
        self.restore_count = 0
        self.max_restores = self.arsenal.storage["RestoreServer"]

        actions = []
        # Randomly deploy decoys on networks
        for i in range(0, num_decoys):
            subnet_to_deploy = self.network.get_random_subnet()
            decoy_name = f"decoy_{i}"
            # IP set by actuator
            decoy_host = Host(decoy_name, "")
            subnet_to_deploy.add_host(decoy_host, decoy=True)

            decoy_action = DeployDecoy(
                sec_group=subnet_to_deploy.sec_group,
                network=subnet_to_deploy.name,
                server=decoy_name,
                host=decoy_host,
                apacheVulnerability=True,
            )
            actions.append(decoy_action)

        # Initialize decoys so we can setup fake credentials
        self.orchestrator.run(actions)

        # Split credentials between subnets
        credentials_per_subnet = int(num_honeycreds / len(self.network.subnets))
        for subnet in self.network.subnets:
            for i in range(0, credentials_per_subnet):
                host = subnet.get_random_host()
                decoy_host = self.network.get_random_decoy()

                # Add fake credentials to decoy
                self.orchestrator.run(
                    [AddHoneyCredentials(host, decoy_host, 1, real=True)]
                )

        self.telemetry_service.subscribe(
            DecoyCredentialUsed, self.handle_decoy_interaction
        )
        self.telemetry_service.subscribe(
            DecoyHostInteraction, self.handle_decoy_interaction
        )
        self.telemetry_service.subscribe(SSHEvent, self.handle_decoy_interaction)

    def handle_decoy_interaction(
        self, event: SSHEvent | DecoyCredentialUsed | DecoyHostInteraction
    ):
        if not isinstance(event, DecoyCredentialUsed):
            self.orchestrator.run([RestoreServer(event.target_ip)])

        self.orchestrator.run([RestoreServer(event.source_ip)])

    # Run actions during the scenario
    def run(self):
        pass
