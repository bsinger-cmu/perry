import docker
from abc import abstractmethod

from ansible.ansible_local_runner import AnsibleLocalRunner


class Image:
    def __init__(self, name, ansible_runner: AnsibleLocalRunner):
        self.name = name
        self.ansible_runner = ansible_runner

    def build(self):
        client = docker.from_env()
        path = "."
        dockerfile = "docker/Dockerfile.env_image"
        tag = self.name.lower()

        client.images.build(
            path=path,
            dockerfile=dockerfile,
            tag=tag,
            buildargs={"IMAGE_NAME": self.name},
        )

    @abstractmethod
    def ansible_provision(self):
        pass
