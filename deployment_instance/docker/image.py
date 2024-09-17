import docker
from abc import abstractmethod

from ansible.ansible_local_runner import AnsibleLocalRunner


class Image:
    def __init__(
        self, name, ansible_runner: AnsibleLocalRunner, start_cmd: str | None = None
    ):
        self.name = name
        self.ansible_runner = ansible_runner

        self.start_cmd = "tail -f /dev/null"
        if start_cmd:
            self.start_cmd = "bash -c '" + start_cmd + " && tail -f /dev/null'"

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

    def run(self):
        client = docker.from_env()
        tag = self.name.lower()

        client.containers.run(
            tag,
            name=self.name,
            command=self.start_cmd,
            detach=True,
            tty=True,
            stdin_open=True,
        )

    @abstractmethod
    def ansible_provision(self):
        pass
