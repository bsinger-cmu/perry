import click
import importlib

from deployment_instance.DeploymentInstance import DeploymentInstance

deployment_instance_module = importlib.import_module("deployment_instance")


@click.group()
@click.option("--type", help="The environment", required=True, type=str)
@click.pass_context
def env(ctx, type: str):
    # Deploy deployment instance
    deployment_instance_ = getattr(deployment_instance_module, type)
    environment: DeploymentInstance = deployment_instance_(
        ctx.obj.ansible_runner,
        ctx.obj.openstack_conn,
        ctx.obj.config.external_ip,
        ctx.obj.config,
    )
    # Add deployment instance to context
    ctx.obj.environment = environment


@env.command()
@click.pass_context
@click.option("--skip_network", help="Skip network setup", is_flag=True)
def setup(ctx, skip_network: bool):
    click.echo("Setting up the environment...")
    if skip_network:
        click.echo("Skipping network setup")
        ctx.obj.environment.runtime_setup()
        # ctx.obj.environment.teardown()
    else:
        ctx.obj.environment.deploy_topology()
        ctx.obj.environment.setup()
        ctx.obj.environment.runtime_setup()


@env.command()
@click.pass_context
@click.option("--skip_network", help="Skip network setup", is_flag=True)
@click.option("--skip_host", help="Skip host setup", is_flag=True)
def compile(ctx, skip_network: bool, skip_host: bool):
    click.echo("Compiling the environment (can take several hours)...")
    ctx.obj.environment.compile(not skip_network, not skip_host)
