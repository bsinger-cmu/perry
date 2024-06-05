from deployment_instance.network import Host
from defender.capabilities import (
    Action,
    DeployDecoy,
    AddHoneyCredentials,
    RestoreServer,
)

from defender.telemetry.events import HighLevelEvent, AttackerOnHost, SSHEvent
from . import Strategy

from utility.logging import log_event


class ReactiveStandalone(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
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
                deploy_host = subnet.get_random_host()
                target_host = self.network.get_random_host()

                # Add fake credentials to decoy
                self.orchestrator.run(
                    [AddHoneyCredentials(deploy_host, target_host, 1, real=False)]
                )

        return []

    # Run actions during the scenario
    def run(self, new_events: list[HighLevelEvent]) -> list[Action]:
        actions = []

        # Process events
        for event in new_events:
            if isinstance(event, AttackerOnHost):
                log_event("Found attacker", f"Attacker on host {event.attacker_ip}")
                if self.max_restores == -1 or self.restore_count < self.max_restores:
                    # Restore host if attacker is detected
                    attacker_ip = event.attacker_ip
                    restoreAction = RestoreServer(attacker_ip)
                    actions.append(restoreAction)
                    self.restore_count += 1

            if isinstance(event, SSHEvent):
                # fmt: off
                log_event("SSH connection detected", f"SSH connection from {event.source_ip} to {event.target_ip}:{event.port}")
                # fmt: on

                if self.network.is_ip_decoy(event.target_ip):
                    if (
                        self.max_restores == -1
                        or self.restore_count < self.max_restores
                    ):
                        # fmt: off
                        log_event("Restoring hosts", f"Restoring host {event.source_ip} after SSH connection detected")
                        # fmt: on

                        # Restore host if SSH connection is detected
                        restoreAction = RestoreServer(event.source_ip)
                        actions.append(restoreAction)
                        self.restore_count += 1

                        # Can restore decoy as many times as you want
                        restoreAction = RestoreServer(event.target_ip)
                        actions.append(restoreAction)

        return actions
