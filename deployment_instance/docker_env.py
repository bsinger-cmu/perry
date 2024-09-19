from abc import abstractmethod

from ansible.ansible_docker_runner import AnsibleDockerRunner


class DockerEnv:

    def __init__(self, ansible_runner: AnsibleDockerRunner):
        self.ansible_runner = ansible_runner

    @abstractmethod
    def setup(self):
        pass
