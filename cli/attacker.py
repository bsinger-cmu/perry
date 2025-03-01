import click

from cli.cli_context import PerryContext
from attacker.Attacker import Attacker
from attacker.config.attacker_config import AttackerConfig, AbstractionLevel


@click.group()
@click.pass_context
@click.option("--strategy", help="The attacker strategy", required=True, type=str)
@click.option("--env", help="The attacker environment", required=True, type=str)
@click.option(
    "--abstraction", help="The level of Perry's abstraction", required=False, type=str
)
def attacker(ctx, strategy: str, env: str, abstraction: str | None):
    context: PerryContext = ctx.obj

    if abstraction is None:
        abstraction = AbstractionLevel.HIGH_LEVEL
    else:
        abstraction = AbstractionLevel(abstraction)

    # Check if env is valid
    # Setup attacker module
    attacker_config = AttackerConfig(
        name=f"{strategy}: {env}",
        strategy=strategy,
        environment=env,
        abstraction=abstraction,
    )

    context.attacker = Attacker(
        context.config.caldera_config.api_key,
        attacker_config,
        context.experiment_id,
    )


@attacker.command()
@click.pass_context
def start(ctx):
    context: PerryContext = ctx.obj
    if context.attacker is None:
        raise Exception("Attacker not initialized")

    click.echo("Starting attacker")
    context.attacker.start_operation()
