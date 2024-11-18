from environment.network import Host
from defender.capabilities import (
    DeployDecoy,
    AddHoneyCredentials,
)

from defender.strategy import Strategy

from utility.logging import log_event


class StaticStandalone(Strategy):
    # Run actions before the scenario starts
    def initialize(self):
        log_event("StaticStandalone", "Initializing StaticStandalone strategy")
        num_decoys = self.arsenal.storage["DeployDecoy"]
        num_honeycreds = self.arsenal.storage["HoneyCredentials"]
        actions = []

        # Try to deploy decoys on webserver network,
        # if not possible, deploy on random subnet
        for i in range(0, num_decoys):
            subnet_to_deploy = self.network.get_subnet_by_name("webserver_network")

            if subnet_to_deploy is None:
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

        # Add fake credentials to all hosts
        credentials_per_subnet = int(num_honeycreds / len(self.network.subnets))
        for subnet in self.network.subnets:
            for i in range(0, credentials_per_subnet):
                deploy_host = subnet.get_random_host()
                target_host = self.network.get_random_host()

                # Add fake credentials to decoy
                self.orchestrator.run(
                    [AddHoneyCredentials(deploy_host, target_host, 1, real=False)]
                )

    # Run actions during the scenario
    def run(self):
        pass
