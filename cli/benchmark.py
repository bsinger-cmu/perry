import click
import importlib
import time

from deployment_instance.DeploymentInstance import DeploymentInstance

deployment_instance_module = importlib.import_module("deployment_instance")


@click.group()
@click.option("--env", help="The environment", required=True, type=str)
@click.pass_context
def bench(ctx, type: str):
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


@bench.command()
@click.pass_context
def setup(ctx):
    click.echo("Setting up the environment...")

    # Time setup for 5 trials
    trials = 5
    times = []
    for _ in range(trials):
        start_time = time.time()
        ctx.obj.environment.find_management_server()
        ctx.obj.environment.parse_network()
        ctx.obj.environment.runtime_setup()
        end_time = time.time()

        trial_time = end_time - start_time
        times.append(trial_time)
        click.echo(f"Trial time: {trial_time}")

    average_time = sum(times) / trials
    click.echo(f"Average time: {average_time}")


@bench.command()
@click.pass_context
def compile(ctx):
    click.echo("Compiling the environment (can take several hours)...")

    # Time compilation for 5 trials
    trials = 5
    times = []

    for _ in range(trials):
        start_time = time.time()
        ctx.obj.environment.compile(True, True)
        end_time = time.time()

        trial_time = end_time - start_time
        times.append(trial_time)
        click.echo(f"Trial time: {trial_time}")

    average_time = sum(times) / trials
    click.echo(f"Average time: {average_time}")
