from deployment_instance.network import Host
from defender.capabilities import (
    Action,
    StartHoneyService,
    DeployDecoy,
    AddHoneyCredentials,
)

from defender.orchestrator.openstack_actuators import (
    AddHoneyCredentials as AddHoneyCredentialsActuator,
)

from defender.telemetry.events import Event
from defender.strategy import Strategy

import random
from utility.logging import log_event


class LayeredEmployee(Strategy):
    # Run actions before the scenario starts
    def initialize(self) -> list[Action]:
        log_event("StaticLayered", "Initializing StaticLayered strategy")
        num_decoys = self.arsenal.storage["DeployDecoy"]
        num_honeycreds = self.arsenal.storage["HoneyCredentials"]

        employee_one_subnet = self.network.get_subnet_by_name("employee_one_network")
        employee_two_subnet = self.network.get_subnet_by_name("employee_two_network")

        if employee_one_subnet is None or employee_two_subnet is None:
            log_event("StaticLayered", "Error could not find employee subnets")
            return []

        subnets_to_deploy = [employee_one_subnet, employee_two_subnet]

        actions = []
        # Randomly deploy decoys on employee networks
        for i in range(0, num_decoys):
            subnet_to_deploy = random.choice(subnets_to_deploy)
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
        credentials_per_subnet = int(num_honeycreds / len(subnets_to_deploy))
        credentialActions = []
        for subnet in subnets_to_deploy:
            for i in range(0, credentials_per_subnet):
                deploy_host = subnet.get_random_host()
                target_host = self.network.get_random_decoy()

                # Add fake credentials to decoy
                credentialActions.append(
                    AddHoneyCredentials(deploy_host, target_host, 1, real=True)
                )

        AddHoneyCredentialsActuator.actuateMany(
            credentialActions, self.orchestrator.ansible_runner
        )

        return []

    # Run actions during the scenario
    def run(self, new_events: list[Event]) -> list[Action]:
        actions = []

        return actions
