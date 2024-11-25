from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
import os
from datetime import datetime

from emulator.emulator import Emulator
from config.Config import Config
from scenarios.Scenario import Experiment

from attacker.exceptions import NoAttackerAgentsError


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
        # Set scenario
        emulator = Emulator(self.config, experiment.scenario)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        experiment_results_dir = f"output/{experiment.scenario}"
        # Check if experiment directory exists
        if not os.path.exists(experiment_results_dir):
            os.makedirs(experiment_results_dir)

        # Task to track progress of trials within the experiment
        trial_task = progress.add_task(
            f"[green]{experiment.scenario} Trials", total=experiment.trials
        )

        for trial in range(experiment.trials):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            experiment_dir = os.path.join(experiment_results_dir, timestamp)
            try:
                emulator.run_trial(experiment_dir, timestamp, experiment.timeout)
            except NoAttackerAgentsError as error:
                print(error)
                # Rerun the trial
                trial -= 1
            progress.update(trial_task, advance=1)

        progress.remove_task(trial_task)
