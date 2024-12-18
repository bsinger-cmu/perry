import click
import importlib

from environment.environment import Environment

env_module = importlib.import_module("environment")


@click.group()
@click.option("--type", help="The environment", required=True, type=str)
@click.pass_context
def env(ctx, type: str):
    # Deploy deployment instance
    deployment_instance_ = getattr(env_module, type)
    environment: Environment = deployment_instance_(
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
        ctx.obj.environment.find_management_server()
        ctx.obj.environment.parse_network()
        ctx.obj.environment.runtime_setup()
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


@env.command()
@click.pass_context
def teardown(ctx):
    click.echo("Tearing down the environment...")
    ctx.obj.environment.teardown()
    click.echo("Environment has been torn down")


@env.command()
@click.pass_context
def deploy_network(ctx):
    click.echo("Setting up network...")
    ctx.obj.environment.deploy_topology()
