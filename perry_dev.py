import click
from deployment_instance.docker.image import Image
from ansible.ansible_local_runner import AnsibleLocalRunner
import importlib

# Load image classes from deployment_instance/docker
image_classes = importlib.import_module("deployment_instance.docker")


@click.group()
def main():
    pass


@main.command()
@click.option(
    "--image_name", type=str, help="Name of the image to build", required=True
)
def build(image_name: str):
    runner = AnsibleLocalRunner("./ansible")
    # Load image
    image_class = getattr(image_classes, image_name)
    image = image_class(image_name, runner)
    image.build()


@main.command()
@click.option(
    "--image_name", type=str, help="Name of the image to build", required=True
)
def run(image_name: str):
    runner = AnsibleLocalRunner("./ansible")
    # Load image
    image_class = getattr(image_classes, image_name)
    image = image_class(image_name, runner)
    image.run()


@main.command()
@click.option(
    "--image_name", type=str, help="Name of the image to build", required=True
)
def provision(image_name: str):
    runner = AnsibleLocalRunner("./ansible")

    # Load image
    image_class = getattr(image_classes, image_name)
    image = image_class(image_name, runner)
    image.ansible_provision()


if __name__ == "__main__":
    main()
