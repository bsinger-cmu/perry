import click
import importlib
from os import path
import json

from cli.cli_context import PerryContext
from scenarios.Scenario import Scenario, Experiment
from emulator.experiment_runner import ExperimentRunner, Emulator

attacker_module = importlib.import_module("attacker")


@click.group()
def experiment():
    pass


@experiment.command()
@click.pass_context
@click.option("--scenario", help="The scenario to run", required=True, type=str)
@click.option(
    "--timeout_min", help="The timeout for the experiment", type=int, default=60
)
def single(ctx, scenario: str, timeout_min: int):
    context: PerryContext = ctx.obj

    with open(path.join("scenarios", "scenarios", scenario), "r") as f:
        scenario_data = json.load(f)
        scenario_obj = Scenario(**scenario_data)

    context.emulator = Emulator(context.config, scenario_obj)

    context.emulator.setup(context.experiment_dir, context.experiment_id)
    context.emulator.run(timeout_min)


@experiment.command()
@click.pass_context
@click.option("--experiment", help="The experiment to run", required=True, type=str)
def batch(ctx, experiment: str):
    context: PerryContext = ctx.obj

    # Load experiment
    experiments = []
    with open(path.join("scenarios/experiments", experiment), "r") as f:
        experiment_raw = json.load(f)
        for experiment_data in experiment_raw:
            experiments.append(Experiment(**experiment_data))

    experiment_runner = ExperimentRunner(experiments, context.config)
    experiment_runner.run()
