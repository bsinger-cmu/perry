from .OpenstackActuator import OpenstackActuator
from defender import capabilities

from ansible.deployment_instance import SetupServerSSHKeys
from ansible.common import CreateUser

from faker import Faker


class AddHoneyCredentials(OpenstackActuator):
    def actuate(self, action: capabilities.AddHoneyCredentials):
        fake = Faker()

        for _ in range(action.number):
            name = fake.name()
            username = name.replace(" ", "")
            password = fake.password()

            # Create user on honey computer
            create_user_pb = CreateUser(action.honey_host.ip, username, password)

            self.ansible_runner.run_playbook(create_user_pb)

            for user in action.credential_host.users:
                ssh_pb = SetupServerSSHKeys(
                    action.credential_host.ip, user, action.honey_host.ip, username
                )

                self.ansible_runner.run_playbook(ssh_pb)
