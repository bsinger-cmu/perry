from .OpenstackActuator import OpenstackActuator
from defender import capabilities

from ansible.deployment_instance import SetupServerSSHKeys, AddToSSHConfig
from ansible.goals import AddData
from ansible.common import CreateUser

from faker import Faker
from utility.logging import get_logger

logger = get_logger()
fake = Faker()


class AddHoneyCredentials(OpenstackActuator):

    @staticmethod
    def getAnsibleActions(action: capabilities.AddHoneyCredentials):
        user_actions = []
        ssh_key_actions = []
        fake_data_actions = []

        for _ in range(action.number):
            name = fake.name()
            username = name.replace(" ", "")
            password = fake.password()

            logger.debug(
                f"Adding honey credentials for {name} on {action.credential_host.name}",
            )

            credential_host_user = CreateUser(
                action.credential_host.ip, username, password
            )
            user_actions.append(credential_host_user)

            if action.real:
                # Create user on honey computer
                create_user_pb = CreateUser(action.honey_host.ip, username, password)
                user_actions.append(create_user_pb)

                for user in action.credential_host.users:
                    ssh_pb = SetupServerSSHKeys(
                        action.credential_host.ip,
                        user,
                        action.honey_host.ip,
                        username,
                    )
                    ssh_key_actions.append(ssh_pb)
                    if action.fakeData:
                        fake_data_pb = AddData(
                            action.honey_host.ip, username, "~/decoy.json"
                        )
                        fake_data_actions.append(fake_data_pb)
            else:
                for user in action.credential_host.users:
                    fake_credential_pb = AddToSSHConfig(
                        action.credential_host.ip, user, action.honey_host.ip, username
                    )
                    ssh_key_actions.append(fake_credential_pb)

        return user_actions, ssh_key_actions, fake_data_actions

    def actuate(self, action: capabilities.AddHoneyCredentials):
        action_priority_list = AddHoneyCredentials.getAnsibleActions(action)

        for action_list in action_priority_list:
            self.ansible_runner.run_playbooks(action_list, run_async=True)

    @staticmethod
    def actuateMany(actions: list[capabilities.AddHoneyCredentials], ansible_runner):
        all_user_actions = []
        all_ssh_key_actions = []
        all_fake_data_actions = []

        for action in actions:
            user_actions, ssh_key_actions, fake_data_actions = (
                AddHoneyCredentials.getAnsibleActions(action)
            )
            all_user_actions.extend(user_actions)
            all_ssh_key_actions.extend(ssh_key_actions)
            all_fake_data_actions.extend(fake_data_actions)

        logger.debug(f"Creating {len(all_user_actions)} users...")
        ansible_runner.run_playbooks(all_user_actions, run_async=False)
        logger.debug(f"Setting up {len(all_ssh_key_actions)} ssh keys...")
        ansible_runner.run_playbooks(all_ssh_key_actions, run_async=True)
        logger.debug(f"Adding {len(all_fake_data_actions)} fake data...")
        ansible_runner.run_playbooks(all_fake_data_actions, run_async=True)
        logger.debug("Done")
