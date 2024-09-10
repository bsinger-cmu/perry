import click
import importlib

from cli.cli_context import PerryContext

attacker_module = importlib.import_module("attacker")


@click.group()
@click.pass_context
@click.option("--type", help="The attacker type", required=True, type=str)
def attacker(ctx, type: str):
    context: PerryContext = ctx.obj

    # Setup attacker module
    caldera_api_key = context.config.caldera_config.api_key
    attacker_ = getattr(attacker_module, type)
    context.attacker = attacker_(caldera_api_key, context.experiment_id)


@attacker.command()
@click.pass_context
def start(ctx):
    context: PerryContext = ctx.obj
    if context.attacker is None:
        raise Exception("Attacker not initialized")

    click.echo("Starting attacker")
    context.attacker.start_operation()
