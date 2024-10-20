from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
import json
import os
from datetime import datetime

from emulator.emulator import Emulator
from config.Config import Config
from scenarios.Scenario import Experiment, Scenario


class ExperimentRunner:
    def __init__(self, experiments: list[Experiment], config: Config):
        self.experiments = experiments
        self.config = config

    def run(self):
        # Initialize a rich progress bar
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ) as progress:

            # Task to track progress of experiments
            experiment_task = progress.add_task(
                "[cyan]Experiments", total=len(self.experiments)
            )

            for experiment in self.experiments:
                self.run_experiment(experiment, progress)
                progress.update(experiment_task, advance=1)

    def run_experiment(self, experiment: Experiment, progress: Progress):
        # Load scenario
        with open(f"scenarios/scenarios/{experiment.scenario}", "r") as f:
            scenario_data = json.load(f)
            scenario_obj = Scenario(**scenario_data)

        # Set scenario
        emulator = Emulator(self.config, scenario_obj)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        experiment_results_dir = f"output/{experiment.name}"
        # Check if experiment directory exists
        if not os.path.exists(experiment_results_dir):
            os.makedirs(experiment_results_dir)

        # Task to track progress of trials within the experiment
        trial_task = progress.add_task(
            f"[green]{experiment.name} Trials", total=experiment.trials
        )

        for trial in range(experiment.trials):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            experiment_dir = os.path.join(experiment_results_dir, timestamp)
            emulator.run_trial(experiment_dir, timestamp, experiment.timeout)
            progress.update(trial_task, advance=1)

        progress.remove_task(trial_task)
