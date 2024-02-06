from .OpenstackActuator import OpenstackActuator
from defender import capabilities

from ansible.deployment_instance import SetupServerSSHKeys
from ansible.common import CreateUser

from faker import Faker
from utility.logging import get_logger

logger = get_logger()


class AddHoneyCredentials(OpenstackActuator):
    def actuate(self, action: capabilities.AddHoneyCredentials):
        fake = Faker()

        for _ in range(action.number):
            name = fake.name()
            username = name.replace(" ", "")
            password = fake.password()

            logger.debug(
                f"Adding honey credentials for {name} on {action.credential_host.name}",
            )

            # Create user on honey computer
            create_user_pb = CreateUser(action.honey_host.ip, username, password)

            self.ansible_runner.run_playbook(create_user_pb)

            for user in action.credential_host.users:
                ssh_pb = SetupServerSSHKeys(
                    action.credential_host.ip, user, action.honey_host.ip, username
                )

                self.ansible_runner.run_playbook(ssh_pb)
