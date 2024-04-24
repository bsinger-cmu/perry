from .OpenstackActuator import OpenstackActuator
from defender import capabilities

from ansible.deployment_instance import SetupServerSSHKeys, AddToSSHConfig
from ansible.defender import SetupFakeCredential
from ansible.common import CreateUser

from faker import Faker
from utility.logging import get_logger

logger = get_logger()


class AddHoneyCredentials(OpenstackActuator):
    def actuate(self, action: capabilities.AddHoneyCredentials):
        fake = Faker()
        user_actions = []
        ssh_key_actions = []

        for _ in range(action.number):
            name = fake.name()
            username = name.replace(" ", "")
            password = fake.password()

            logger.debug(
                f"Adding honey credentials for {name} on {action.credential_host.name}",
            )

            # Create user on honey computer
            create_user_pb = CreateUser(action.honey_host.ip, username, password)
            credential_host_user = CreateUser(
                action.credential_host.ip, username, password
            )
            user_actions.append(create_user_pb)
            user_actions.append(credential_host_user)

            if action.real:
                for user in action.credential_host.users:
                    ssh_pb = SetupServerSSHKeys(
                        action.credential_host.ip, user, action.honey_host.ip, username
                    )
                    ssh_key_actions.append(ssh_pb)
            else:
                for user in action.credential_host.users:
                    fake_credential_pb = AddToSSHConfig(
                        action.credential_host.ip, user, action.honey_host.ip, username
                    )
                    ssh_key_actions.append(fake_credential_pb)

        self.ansible_runner.run_playbooks(user_actions, run_async=True)

        # Adding to config can be in async
        # Setting up server ssh keys cannot be async because keys have to download to this machine
        if action.real:
            self.ansible_runner.run_playbooks(ssh_key_actions, run_async=False)
        else:
            self.ansible_runner.run_playbooks(ssh_key_actions, run_async=True)
