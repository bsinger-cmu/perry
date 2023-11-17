from emulator import Emulator
from colorama import Fore, Back, Style

import yaml
import os
from os import path
import re
from console import progress
from rich import print as rprint
import argparse
import copy
from utility.logging import get_logger, log_event

import json
from scenarios import Experiment, Scenario

logger = get_logger()

from typing import NoReturn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


class EmulatorInteractive:
    def __init__(self, emulator: Emulator, config=None, scenario=None):
        self.emulator = emulator
        self.config = config
        self.scenario = scenario
        self.loaded_experiment = None
        self.all_experiments: list[Experiment] = []

        self.session = PromptSession(history=FileHistory(".emulator_history"))

        self.emulator_parser = ArgumentParser(
            prog="emulator",
            add_help=False,
            exit_on_error=False,
        )
        subparsers = self.emulator_parser.add_subparsers()

        run_parser = subparsers.add_parser("run", help="run the attacker")
        run_parser.add_argument(
            "-n", "--num", help="number of times to run attacker", type=int, default=1
        )
        run_parser.add_argument(
            "-s",
            "--suppress-metrics",
            help="do not print metrics",
            default=False,
            action="store_true",
        )
        run_parser.add_argument(
            "-q",
            "--quiet",
            help="do not print any ansible information",
            default=False,
            action="store_true",
        )
        run_parser.set_defaults(func=self.handle_run)

        help_parser = subparsers.add_parser("help", help="print help message")
        help_parser.set_defaults(func=self.handle_help)

        exit_parser = subparsers.add_parser("exit", help="exit emulator")
        exit_parser.set_defaults(func=self.handle_exit)

        setup_parser = subparsers.add_parser("setup", help="setup scenario")
        setup_parser.add_argument(
            "-c", "--config", help="Name of configuration file", required=True
        )
        setup_parser.add_argument(
            "-s", "--scenario", help="Name of scenario file", required=True
        )
        setup_parser.add_argument(
            "-o", "--output", help="Output subdir for metrics", default=None
        )
        setup_parser.set_defaults(func=self.handle_setup)

        load_parser = subparsers.add_parser(
            "load", help="load from experiment config file"
        )
        load_parser.add_argument(
            "-c", "--config", help="Name of configuration file", required=True
        )
        load_parser.add_argument("file", help="Name of batch scenario file", type=str)
        load_parser.add_argument(
            "-s",
            "--strict",
            help="Requires all experiments to have required, valid fields",
            action="store_true",
            default=False,
        )
        load_parser.set_defaults(func=self.handle_load)

        execute_parser = subparsers.add_parser(
            "execute", help="execute loaded experiments"
        )
        execute_parser.add_argument(
            "-s",
            "--suppress-metrics",
            help="do not print metrics",
            default=False,
            action="store_true",
        )
        execute_parser.add_argument(
            "-q",
            "--quiet",
            help="do not print any ansible information",
            default=False,
            action="store_true",
        )
        execute_parser.set_defaults(func=self.handle_execute)

        view_parser = subparsers.add_parser("view", help="view current settings")
        view_parser.add_argument(
            "setting", choices=["config", "scenario", "experiments", "metrics"]
        )
        view_parser.set_defaults(func=self.handle_view)

        compile_parser = subparsers.add_parser(
            "compile", help="compile deployment instance"
        )
        compile_parser.add_argument(
            "-n",
            "--network-only",
            help="compiles just network",
            default=False,
            action="store_true",
        )
        compile_parser.set_defaults(func=self.handle_compile)

    def start_interactive_emulator(self):
        """
        start_interactive_emulator:
        starts interactive mode
        """
        print("Starting interactive emulator...")
        print("Type 'help' for a list of commands")
        while True:
            user_input = self.session.prompt(
                "emulator> ", auto_suggest=AutoSuggestFromHistory()
            )

            emulator_argv = user_input.split(" ")

            try:
                args = self.emulator_parser.parse_args(emulator_argv)
                if not ("--help" in emulator_argv or "-h" in emulator_argv) and hasattr(
                    args, "func"
                ):
                    args.func(args)
            except argparse.ArgumentError as e:
                print(e)
                self.emulator_parser.print_help()

    def load_config_and_scenario(self, config, scenario):
        """
        load_config_and_scenario:
        Open the config and scenario files and return the yaml contents
        """
        with open(path.join("config", config), "r") as f:
            config = yaml.safe_load(f)

        # open yml config file
        with open(path.join("scenarios", "scenarios", scenario), "r") as f:
            scenario = json.load(f)
            scenario = Scenario(**scenario)
        return (config, scenario)

    def run_experiment_trial(self, experiment_output_dir):
        """
        run_experiment_trial:
        This function will run a single trial of the experiment loaded.
        """
        result = None
        try:
            load = self.emulator.setup(experiment_output_dir)
        except Exception as e:
            print(f"{Back.RED}Failed with exception:{Style.RESET_ALL}")
            print(e)
            result = ("Exception", e)

            logger.error("Failed to run experiment", exc_info=True)
            log_event("FAILURE", str(e))

        if load == 1:  # Failed to load snapshots. Skip this run
            print(f"{Fore.RED}Failed to load snapshots{Style.RESET_ALL}")
            result = ("Error", "Failed to load snapshots")

        if result is None:
            try:
                metrics = self.emulator.run()
            except Exception as e:
                print(f"{Back.RED}Failed with exception:{Style.RESET_ALL}")
                print(e)
                result = ("Exception", e)

        if result is None:
            result = ("Success", metrics)
        return result

    def print_all_metrics(
        self, all_metrics, trials, complete_count, error_count, exception_count
    ):
        """
        print_all_metrics
        Print all metrics for multiple runs of the experiment
        """
        print(f"\nCompleted all experiment trials. Printing statuses...")
        for j in range(trials):
            metrics = all_metrics[j][0]
            if metrics == "Error":
                print(f"Run {j+1}: {Fore.RED}Failed to load snapshots{Style.RESET_ALL}")
            elif metrics == "Exception":
                print(
                    f"Run {j+1}: {Back.RED}Failed with exception:{Style.RESET_ALL}\n{all_metrics[j][1]}"
                )
            else:
                print(
                    f"Run {j+1}: {Fore.GREEN}Successfully ran to completion{Style.RESET_ALL}"
                )
                # rprint(metrics)
        print(
            f"{Fore.CYAN}Total number of experiments runs:{Style.RESET_ALL}     {trials}"
        )
        print(
            f"Times {Fore.GREEN}to completion:{Style.RESET_ALL}                  {complete_count}"
        )
        if error_count > 0:
            print(
                f"Times {Fore.RED}failed to load snapshots:{Style.RESET_ALL}       {error_count}"
            )
        if exception_count > 0:
            print(
                f"Times {Back.RED}failed with exception:{Style.RESET_ALL}          {exception_count}"
            )

    def handle_setup(self, args):
        """
        handle_setup
        This function will handle the setup command and load the config and scenario files.
        """
        (config, scenario) = self.load_config_and_scenario(args.config, args.scenario)
        self.emulator.set_output_subdir(args.output)
        self.emulator.set_config(config)
        self.emulator.set_scenario(scenario)
        return

    def handle_compile(self, args):
        self.emulator.setup(compile=True, network_only=args.network_only)

    def handle_run(self, args):
        """
        handle_run:
        This function will handle the run command.
        It will run the attacker for the specified number of trials for the setup
        scenario and config files loaded by the setup command
        """
        if self.emulator.config is None or self.emulator.scenario is None:
            print("No config or scenario loaded. Run 'setup' command first")
            return

        self.emulator.set_quiet(args.quiet)
        # num = args.num
        trials = args.num
        all_metrics = []

        rprint(f"Running {trials} trials...")
        complete_count = 0
        error_count = 0
        exception_count = 0
        experiment_task = progress.add_task(
            "[yellow]Running Experiment Trials", start=False, total=trials
        )

        with progress:
            progress.start_task(experiment_task)
            for i in range(trials):
                rprint(f"Starting trial... {i+1}/{trials}")
                result = self.run_experiment_trial()

                status = result[0]
                if status == "Success":
                    complete_count += 1
                elif status == "Error":
                    error_count += 1
                elif status == "Exception":
                    exception_count += 1

                all_metrics.append(result)
                progress.update(experiment_task, refresh=True, advance=1)
            progress.update(
                experiment_task, description="[green]Completed Experiment Trials"
            )

        progress.remove_task(experiment_task)

        # Print metrics for multiple runs
        if not args.suppress_metrics:
            self.print_all_metrics(
                all_metrics, trials, complete_count, error_count, exception_count
            )

    def handle_execute(self, args):
        """
        handle execute
        This function will handle the execute command.
        It will run all trials of all experiments loaded from the configuration file.
        """
        if self.loaded_experiment is None:
            print("No experiments loaded. Load experiments first using 'load' command")
            return

        num_exps = len(self.all_experiments)
        num_trials = sum([exp.trials for exp in self.all_experiments])
        all_trials_task = progress.add_task(
            "[white]Total Trials Completed", start=False, total=num_trials
        )
        all_experiments_task = progress.add_task(
            "[cyan]Running All Experiments", start=False, total=num_exps
        )
        experiment_task = progress.add_task(
            f"[yellow]Running Experiment", start=False, total=None
        )
        all_subtasks = []
        all_experiments_outcome = {}

        self.emulator.set_quiet(args.quiet)

        # Use progress bar to show the progress of all experiments
        with progress:
            progress.start_task(all_experiments_task)
            progress.start_task(all_trials_task)
            for experiment in self.all_experiments:
                # Load/Setup each experiment
                (config, scenario) = self.load_config_and_scenario(
                    self.config, experiment.scenario
                )
                self.emulator.set_config(config)
                self.emulator.set_scenario(scenario)

                experiment_output_dir = path.join("output", experiment.name)

                # Reset trials and counts
                trials = experiment.trials
                complete_count = 0
                error_count = 0
                exception_count = 0
                all_metrics = []

                is_halted = False
                exp_id = experiment.name

                all_subtasks.append(experiment_task)
                progress.update(
                    experiment_task,
                    description=f"[yellow]Running Experiment {exp_id}",
                    total=trials,
                    start=False,
                    completed=0,
                )
                progress.start_task(experiment_task)
                for i in range(trials):
                    # Run each trial of the current experiment
                    rprint(f"Starting trial... {i+1}/{trials}")

                    result = self.run_experiment_trial(experiment_output_dir)
                    all_metrics.append(result)
                    status = result[0]
                    if status == "Success":
                        complete_count += 1
                    elif status == "Error":
                        error_count += 1
                    elif status == "Exception":
                        exception_count += 1

                    progress.update(experiment_task, advance=1)
                    progress.update(all_trials_task, advance=1)
                    progress.update(all_experiments_task, advance=1 / trials)

                # set the outcome + metrics of the current experiment
                all_experiments_outcome[exp_id] = {
                    "all_metrics": all_metrics,
                    "trials": trials,
                    "complete_count": complete_count,
                    "error_count": error_count,
                    "exception_count": exception_count,
                }

                # If experiment is halted, set the color of bar to red
                if is_halted:
                    progress.update(
                        experiment_task, description=f"[red]Halted Experiment {exp_id}"
                    )
                else:
                    progress.update(
                        experiment_task,
                        description=f"[green]Completed Experiment {exp_id}",
                    )
                progress.reset(
                    experiment_task,
                    description=f"[yellow]Running Experiment {exp_id}",
                    start=False,
                )

        progress.remove_task(all_experiments_task)
        progress.remove_task(all_trials_task)
        progress.remove_task(experiment_task)

        if not args.suppress_metrics:
            print(
                f"\nCompleted all experiments from config {self.loaded_experiment}. Printing statuses..."
            )
            for exp in self.all_experiments:
                print(f"\nExperiment {exp.name}")
                if exp.name in all_experiments_outcome.keys():
                    self.print_all_metrics(**all_experiments_outcome[exp.name])

    def handle_exit(self, _):
        print("Exiting emulator...")
        exit()

    def handle_help(self, _):
        self.emulator_parser.print_help()

    def handle_view(self, args):
        """
        View current settings: config, scenario, experiments
        """
        if args.setting == "config":
            if self.emulator.config is None:
                print("No config loaded")
                return
            rprint(self.emulator.config)

        elif args.setting == "scenario":
            if self.emulator.scenario is None:
                print("No scenario loaded")
                return
            rprint(self.emulator.scenario)

        elif args.setting == "experiments":
            if self.all_experiments is None:
                print("No experiment config loaded")
                return
            rprint(self.all_experiments)

        elif args.setting == "metrics":
            if self.all_experiments is None:
                print("No experiment config loaded")
                return
            rprint(self.all_experiments)

        else:
            print("Invalid option")

    def handle_load(self, args):
        """
        handle_load
        This function will handle the load command.
        Load experiments from a configuration file.
        This also uses the default configuration file to fill in missing fields.
        """
        if args.file is None:
            print("No experiment specified")
            return

        if args.config is None:
            print("No config file specified")
            return

        self.loaded_experiment = args.file
        self.config = args.config

        experiments = []
        with open(path.join("scenarios", "experiments", args.file), "r") as f:
            # read as json
            exp_data = json.load(f)
            for experiment in exp_data:
                experiments.append(Experiment(**experiment))

        self.all_experiments = experiments
        for experiment in self.all_experiments:
            # Format experiment contents
            rprint(experiment)

        return


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(None, message)

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        if status == 0:
            return
        print("EXIT", status, message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="Name of configuration file", required=False
    )
    parser.add_argument(
        "-s", "--scenario", help="Name of scenario file", required=False
    )

    parser.add_argument(
        "-i",
        "--interactive",
        help="Run emulator in interactive mode",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-o", "--output", help="Output subdir in metrics dir", default=None
    )

    parser.add_argument(
        "-r",
        "--redeploy-hosts",
        help="Re-execute all setup tasks without using snapshots",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-R",
        "--redeploy-network",
        help="Redeploy network topology",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-t", "--test", help="placeholder", action="store_true", default=False
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="(ALWAYS ON). debug mode",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    # if args.test:
    #     test_task = progress.add_task("[yellow]Running Experiment Trials", start=False, total=10)
    #     with progress:
    #         progress.start_task(test_task)
    #         for i in range(10):
    #             progress.update(test_task, refresh=True, advance=1)
    #             time.sleep(4.3)
    #     exit(0)

    print(
        f"Starting emulator in {'' if args.interactive else 'non-'}interactive mode..."
    )

    if args.debug:
        rprint("This flag is currently inactive. Debug mode always on. Ignoring...")

    # open yml config file
    if args.config:
        with open(path.join("config", args.config), "r") as f:
            config = yaml.safe_load(f)

    # open yml config file
    if args.scenario:
        with open(path.join("scenarios", args.scenario), "r") as f:
            scenario = yaml.safe_load(f)

    emulator = Emulator()

    if args.output:
        emulator.set_output_subdir(args.output)

    if args.interactive:
        if args.redeploy_hosts:
            emulator.setup(
                config,
                scenario,
                redeploy_hosts=args.redeploy_hosts,
                redeploy_network=args.redeploy_network,
            )

        if args.scenario:
            emulator.scenario = scenario
        if args.config:
            emulator.config = config
        EmulatorInteractive(emulator).start_interactive_emulator()

    else:
        emulator.setup(
            config,
            scenario,
            redeploy_hosts=args.redeploy_hosts,
            redeploy_network=args.redeploy_network,
        )
        emulator.run()

        # Print metrics
        emulator.goalkeeper.print_metrics()
        emulator.attacker.cleanup()
