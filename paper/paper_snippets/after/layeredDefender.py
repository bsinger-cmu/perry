# Ignore type hinting
# type: ignore

from HighLevelObservations import (
    TelemetryModule,
    HostInteractedWithDecoyHost,
    HostUsedDecoyCredential,
)
from HighLevelActions import (
    HighLevelAction,
    DeployDecoy,
    RestoreServer,
    AddHoneyCredentials,
)
from EnvironmentStateService import EnvironmentStateService


class ReactiveLayered(Strategy):

    ### (1) Initialize layered deception strategy ###
    # Randomly deploy decoys on networks
    for _ in range(0, num_decoys):
        subnet_to_deploy = EnvironmentStateService.get_random_subnet()

        DeployDecoy(
            network=subnet_to_deploy.name,
            host=decoy_host,
        ).execute()

    # Randomly deploy decoys on networks
    for _ in range(0, num_honeycreds):
        deploy_host = EnvironmentStateService.get_random_host()
        target_host = EnvironmentStateService.get_random_decoy()

        # Add fake credentials to decoy
        AddHoneyCredentials(deploy_host, target_host, real=True).execute()

    ### (2) Detect attackers interacting with decoy resources ###
    TelemetryModule.subscribe(
        HostInteractedWithDecoyHost, self.handle_decoy_host_interaction
    )
    TelemetryModule.subscribe(
        HostUsedDecoyCredential, self.handle_decoy_host_interaction
    )

    ### (3) React to attacker behavior ###
    # Restore server after attacker interacts with decoy host
    def handle_decoy_host_interaction(
        self, event: HostInteractedWithDecoyHost
    ) -> list[HighLevelAction]:
        return [
            # High-level actions to restore server
            RestoreServer(event.source_ip),
            RestoreServer(event.target_ip),
        ]

    # Restore server after attacker uses decoy credential
    def handle_decoy_credential_used(
        self, event: HostUsedDecoyCredential
    ) -> list[HighLevelAction]:
        return [
            RestoreServer(event.source_ip),
        ]
