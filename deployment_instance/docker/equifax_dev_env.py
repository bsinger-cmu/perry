from deployment_instance.docker_env import DockerEnv

from ansible.caldera.InstallAttacker import InstallAttacker


class EquifaxDevEnv(DockerEnv):

    def setup(self):
        self.ansible_runner.run_playbook(
            InstallAttacker("192.168.200.2", "root", "localhost:8888")
        )
