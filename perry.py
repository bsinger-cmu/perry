import click
import openstack
import json
from datetime import datetime
import os

from ansible.AnsibleRunner import AnsibleRunner
from config.Config import Config
from cli.attacker import attacker
from cli.environment import env
from cli.cli_context import PerryContext


@click.group()
@click.pass_context
def main(ctx):
    # Load the configuration
    with open("config/config.json", "r") as file:
        config = Config(**json.load(file))

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    experiment_dir = f"./output/misc/{timestamp}"
    # Create the experiment directory
    os.makedirs(experiment_dir, exist_ok=True)

    openstack_conn = openstack.connect(cloud="default")
    ansible_runner = AnsibleRunner(
        config.openstack_config.ssh_key_path,
        None,
        "./ansible/",
        experiment_dir,
        False,
    )

    # Add to context
    perry_util = PerryContext(
        openstack_conn, ansible_runner, config, experiment_dir, experiment_id=timestamp
    )
    ctx.obj = perry_util


main.add_command(attacker)
main.add_command(env)


if __name__ == "__main__":
    main()
