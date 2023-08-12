import argparse
import copy
import os
from typing import NoReturn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from AnsibleRunner import AnsibleRunner
from deployment_instance import SimpleInstanceV1, GoalKeeper

import openstack

import time
from datetime import datetime

# Dynamically import modules
import importlib
deployment_instance_module = importlib.import_module('deployment_instance')
defender_module = importlib.import_module('defender')
attacker_module = importlib.import_module('attacker')

from attacker import Attacker, TwoPathAttacker
from defender import WaitAndSpotDefender, Defender

from rich import print as rprint
from console import console, progress
from rich.progress import track
import rich.progress as rpg
import re

from os import path
import yaml
from elasticsearch import Elasticsearch

from colorama import Fore, Back, Style

class Emulator:

    def __init__(self):
        self.openstack_conn = openstack.connect(cloud='default')

        self.scenario = None
        self.config = None
        self.output_subdir = None
        self.quiet = False


    def set_quiet(self, quiet):
        self.quiet = quiet

    def set_config(self, config):
        self.config = config

    def set_scenario(self, scenario):
        self.scenario = scenario

    def safe_create_dir(self, dir_path):
        """
        safely create a directory
        """
        if not path.exists(dir_path):
            print(f"Creating directory {dir_path}")
            try:
                os.makedirs(dir_path)
            except OSError as e:
                print(f"Error creating directory {dir_path}: {e}")
                return

    def set_output_subdir(self, subdir):
        """
        set the output directory and ensure that the results and metrics directories exist
        If not, create them
        """
        if subdir is not None:
            self.output_subdir = subdir
            dirs_to_make = [os.path.join('results', subdir), os.path.join('metrics', subdir)]

            for dir_to_make in dirs_to_make:
                self.safe_create_dir(dir_to_make)


    def setup(self, config, scenario, redeploy_hosts=False, new_flags=False, redeploy_network=True):
        # Setup connection to elasticsearch
        elasticsearch_server = f"https://localhost:{config['elasticsearch']['port']}"
        elasticsearch_api_key = config['elasticsearch']['api_key']

        elasticsearch_conn = Elasticsearch(
            elasticsearch_server,
            basic_auth=("elastic", elasticsearch_api_key),
            verify_certs=False
        )

        # Delete all decoy instances on openstack
        all_servers = self.openstack_conn.list_servers()
        deleted_decoys = False
        for server in all_servers:
            if 'decoy' in server.name:
                print(f"Deleting decoy server: {server.name}")
                self.openstack_conn.delete_server(server.id)
                deleted_decoys = True
        if deleted_decoys:
            time.sleep(5)

        # Initialize ansible
        ssh_key_path = config['ssh_key_path']
        ansible_dir = './ansible/'
        ansible_runner = AnsibleRunner(ssh_key_path, None, ansible_dir, self.quiet)

        self.scenario = scenario
        self.config = config

        # Setup attacker
        caldera_api_key = config['caldera']['api_key']
        self.caldera_api_key = caldera_api_key
        attacker_ = getattr(attacker_module, scenario['attacker'])
        self.attacker = attacker_(caldera_api_key)

        # Setup GoalKeeper
        self.goalkeeper = GoalKeeper(self.attacker)
        self.goalkeeper.start_setup_timer()

        # Deploy deployment instance
        deployment_instance_ = getattr(deployment_instance_module, scenario['deployment_instance'])
        self.deployment_instance = deployment_instance_(ansible_runner, self.openstack_conn, config['external_ip'])
        
        load = self.deployment_instance.setup(redeploy_hosts=redeploy_hosts, redeploy_network=redeploy_network, new_flags=new_flags)
        if load == 1: ## Failure to load snapshots
            return load
        
        self.deployment_instance.print_all_flags()

        self.goalkeeper.set_flags(self.deployment_instance.flags)
        self.goalkeeper.set_root_flags(self.deployment_instance.root_flags)

        
        # Setup initial defender
        defender_ = getattr(defender_module, scenario['defender']['type'])
        arsenal_ = getattr(defender_module, scenario['defender']['arsenal']['type'])
        arsenal = arsenal_(scenario['defender']['arsenal'])

        self.defender = defender_(ansible_runner, self.openstack_conn, elasticsearch_conn, config['external_ip'], config['elasticsearch']['port'], config['elasticsearch']['api_key'], arsenal)
        #self.defender = Defender(ansible_runner, self.openstack_conn, elasticsearch_conn, config['external_ip'], config['elasticsearch']['port'], config['elasticsearch']['api_key'])
        self.defender.start()
        self.goalkeeper.stop_setup_timer()

    # Start attacker
    def start_attacker(self):
        self.attacker.start_operation()
        self.goalkeeper.operation_id = self.attacker.operation_id
        print("Operation ID: " + self.attacker.operation_id)

    def finished(self):
        return not self.attacker.still_running()

    def start_main_loop(self):
        print('Main loop starting!')
        finished = False
        finish_counter = 0
        try:
            while not finished:
                self.defender.run()

                if finish_counter > 5:
                    finish_counter = 0
                    # Check if attacker has finished
                    finished = self.finished()

                time.sleep(.5)
                finish_counter += 1
        
        except KeyboardInterrupt:
            pass

    def run(self):
        """
        start running the emulator.
        This does the setup and then runs the attacker and main loop
        """
        time.sleep(5)
        self.goalkeeper.start_execution_timer()

        self.start_attacker()
        # Runs loop until emulation finishes
        self.start_main_loop()
        self.goalkeeper.stop_execution_timer()
        # Once finished calculate have goalkeeper measure final success metrics
        self.goalkeeper.calculate_metrics()
        self.goalkeeper.set_metric('deployment_instance', self.scenario['deployment_instance'])
        self.goalkeeper.set_metric('attacker', self.scenario['attacker'])
        self.goalkeeper.set_metric('defender', self.scenario['defender']['type'])

        self.goalkeeper.metrics = self.goalkeeper.metrics | self.defender.metrics
        
        print("Attacker finished!")
        self.goalkeeper.print_metrics()
        # Cleanup
        
        print("Cleaning up attacker...")
        self.attacker.cleanup()

        print("Saving metrics...")
        self.goalkeeper.save_metrics(subdir=self.output_subdir)
        return self.goalkeeper.metrics

    # Call if using an external stepper for the defender
    # Example: You want OpenAI gym to control the defender for learning a new policy
    def external_defender_steps(self, actions):
        return self.defender.run(actions)



class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(None, message)

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        if status == 0:
            return
        print("EXIT", status, message)


class EmulatorInteractive():
    def __init__(self, emulator, config=None, scenario=None):
        self.emulator = emulator
        self.config = config
        self.scenario = scenario
        self.loaded_config = None
        self.all_experiments = []


        self.session = PromptSession(history=FileHistory('.emulator_history'))

        self.emulator_parser = ArgumentParser(prog="emulator", add_help=False, exit_on_error=False,)
        subparsers = self.emulator_parser.add_subparsers()

        run_parser = subparsers.add_parser('run', help='run the attacker')
        run_parser.add_argument('-n', '--num', help='number of times to run attacker', type=int, default=1)
        run_parser.add_argument('-s', '--suppress-metrics', help='do not print metrics', default=False, action="store_true")
        run_parser.add_argument('-q', '--quiet', help='do not print any ansible information', default=False, action="store_true")
        run_parser.set_defaults(func=self.handle_run)

        help_parser = subparsers.add_parser('help', help='print help message')
        help_parser.set_defaults(func=self.handle_help)

        exit_parser = subparsers.add_parser('exit', help='exit emulator')
        exit_parser.set_defaults(func=self.handle_exit)

        setup_parser = subparsers.add_parser('setup', help='setup scenario')
        setup_parser.add_argument('-c', '--config', help='Name of configuration file', required=True)
        setup_parser.add_argument('-s', '--scenario', help='Name of scenario file', required=True)
        setup_parser.add_argument('-o', '--output', help='Output subdir for metrics', default=None)
        setup_parser.set_defaults(func=self.handle_setup)

        load_parser = subparsers.add_parser('load', help='load from experiment config file')
        load_parser.add_argument('file', help='Name of experiment config file', type=str)
        load_parser.add_argument('-s', '--strict', help='Requires all experiments to have required, valid fields', action='store_true', default=False)
        load_parser.set_defaults(func=self.handle_load)

        execute_parser = subparsers.add_parser('execute', help='execute loaded experiments')
        execute_parser.add_argument('-s', '--suppress-metrics', help='do not print metrics', default=False, action="store_true")
        execute_parser.add_argument('-q', '--quiet', help='do not print any ansible information', default=False, action="store_true")
        execute_parser.set_defaults(func=self.handle_execute)

        view_parser = subparsers.add_parser('view', help='view current settings')
        view_parser.add_argument('setting', choices=['config', 'scenario', 'experiments', 'metrics'])
        view_parser.set_defaults(func=self.handle_view)


    def start_interactive_emulator(self):
        """
        start_interactive_emulator:
        starts interactive mode
        """
        print("Starting interactive emulator...")
        print("Type 'help' for a list of commands")
        while True:
            user_input = self.session.prompt("emulator> ", auto_suggest=AutoSuggestFromHistory())

            emulator_argv = user_input.split(" ")

            try:
                args = self.emulator_parser.parse_args(emulator_argv)
                if not ('--help' in emulator_argv or '-h' in emulator_argv) and hasattr(args, 'func'):
                    args.func(args)
            except argparse.ArgumentError as e:
                print(e)
                self.emulator_parser.print_help()


    def load_config_and_scenario(self, config, scenario):
        """
        load_config_and_scenario:
        Open the config and scenario files and return the yaml contents
        """
        with open(path.join('config', config), 'r') as f:
            config = yaml.safe_load(f)

        # open yml config file
        with open(path.join('scenarios', scenario), 'r') as f:
            scenario = yaml.safe_load(f)
        return (config, scenario)

    
    def run_experiment_trial(self):
        """
        run_experiment_trial:
        This function will run a single trial of the experiment loaded.
        """
        result = None
        try:
            load = self.emulator.setup(self.emulator.config, self.emulator.scenario)
        except Exception as e:
            print(f"{Back.RED}Failed with exception:{Style.RESET_ALL}")
            print(e)
            result = ("Exception", e)

        if load == 1: # Failed to load snapshots. Skip this run
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


    def print_all_metrics(self, all_metrics, trials, complete_count, error_count, exception_count):
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
                print(f"Run {j+1}: {Back.RED}Failed with exception:{Style.RESET_ALL}\n{all_metrics[j][1]}")
            else:
                print(f"Run {j+1}: {Fore.GREEN}Successfully ran to completion{Style.RESET_ALL}")
                # rprint(metrics)
        print(f"{Fore.CYAN}Total number of experiments runs:{Style.RESET_ALL}     {trials}")
        print(f"Times {Fore.GREEN}to completion:{Style.RESET_ALL}                  {complete_count}")
        if error_count > 0:
            print(f"Times {Fore.RED}failed to load snapshots:{Style.RESET_ALL}       {error_count}")
        if exception_count > 0:
            print(f"Times {Back.RED}failed with exception:{Style.RESET_ALL}          {exception_count}")


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
        experiment_task = progress.add_task("[yellow]Running Experiment Trials", start=False, total=trials)

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
            progress.update(experiment_task,description="[green]Completed Experiment Trials")

        progress.remove_task(experiment_task)
        
        # Print metrics for multiple runs
        if not args.suppress_metrics:
            self.print_all_metrics(all_metrics, trials, complete_count, error_count, exception_count)
    


    def handle_execute(self, args):
        """
        handle execute
        This function will handle the execute command.
        It will run all trials of all experiments loaded from the configuration file.
        """
        if self.loaded_config is None:
            print("No experiments loaded. Load experiments first using 'load' command")
            return

        num_exps = len(self.all_experiments)
        num_trials = sum([exp['trials'] for exp in self.all_experiments])
        all_trials_task = progress.add_task("[white]Total Trials Completed", start=False, total=num_trials)
        all_experiments_task = progress.add_task("[cyan]Running All Experiments", start=False, total=num_exps)
        experiment_task = progress.add_task(f"[yellow]Running Experiment", start=False, total=None)
        all_subtasks = []
        all_experiments_outcome = {}

        self.emulator.set_quiet(args.quiet)

        # Use progress bar to show the progress of all experiments
        with progress:
            progress.start_task(all_experiments_task)
            progress.start_task(all_trials_task)
            for experiment in self.all_experiments:
                # Load/Setup each experiment
                (config, scenario) = self.load_config_and_scenario(experiment['setup']['config'], experiment['setup']['scenario'])
                self.emulator.set_config(config)
                self.emulator.set_scenario(scenario)
                if experiment['flags']['use_subdir'] == True:
                    self.emulator.set_output_subdir(experiment['output']['subdir'])
                
                # Reset trials and counts
                trials = experiment['trials']
                complete_count = 0
                error_count = 0
                exception_count = 0
                all_metrics = []

                is_halted = False
                exp_id = experiment['id']

                max_exceptions = experiment['settings']['max_exceptions']
                max_errors = experiment['settings']['max_errors']
                max_retries = experiment['settings']['max_retries']

                all_subtasks.append(experiment_task)

                if experiment['flags']['redeploy_hosts'] == True or experiment['flags']['redeploy_network'] == True:
                    self.emulator.setup(self.emulator.config, self.emulator.scenario, 
                                        redeploy_hosts=experiment['flags']['redeploy_hosts'], 
                                        redeploy_network=experiment['flags']['redeploy_network'])
                
                
                progress.update(experiment_task, description=f"[yellow]Running Experiment {exp_id}", total=trials, start=False, completed=0)
                progress.start_task(experiment_task)
                for i in range(trials):
                    # Run each trial of the current experiment
                    rprint(f"Starting trial... {i+1}/{trials}")
                    
                    result = self.run_experiment_trial()
                    all_metrics.append(result)
                    status = result[0]
                    if status == "Success":
                        complete_count += 1
                    elif status == "Error":
                        error_count += 1
                    elif status == "Exception":
                        exception_count += 1

                    if max_errors > 0 and error_count > max_errors:
                        print(f"{Fore.RED}Max {max_errors} errors exceeded in trial {i+1}. Halting experiment {exp_id}{Style.RESET_ALL}")
                        progress.stop_task(experiment_task)
                        is_halted = True
                        break

                    if max_exceptions > 0 and exception_count > max_exceptions:
                        print(f"{Fore.RED}Max {max_exceptions} exceptions exceeded in trial {i+1}. Halting experiment {exp_id}{Style.RESET_ALL}")
                        progress.stop_task(experiment_task)
                        is_halted = True
                        break

                    progress.update(experiment_task, advance=1)
                    progress.update(all_trials_task, advance=1)
                    progress.update(all_experiments_task, advance=1/trials)    
                

                # set the outcome + metrics of the current experiment
                all_experiments_outcome[exp_id] = {"all_metrics": all_metrics, 
                                                "trials": trials, 
                                                "complete_count": complete_count, 
                                                "error_count": error_count, 
                                                "exception_count": exception_count}
                
                # If experiment is halted, set the color of bar to red
                if is_halted: 
                    progress.update(experiment_task, description=f"[red]Halted Experiment {exp_id}")
                else:
                    progress.update(experiment_task, description=f"[green]Completed Experiment {exp_id}")
                progress.reset(experiment_task, description=f"[yellow]Running Experiment {exp_id}", start=False)

        
        progress.remove_task(all_experiments_task)
        progress.remove_task(all_trials_task)
        progress.remove_task(experiment_task)

        if not args.suppress_metrics:
            print(f"\nCompleted all experiments from config {self.loaded_config}. Printing statuses...")
            for exp in self.all_experiments:
                print(f"\nExperiment {exp['id']}")
                print(f"{exp['name']}: {exp['description']}")
                if exp['id'] in all_experiments_outcome.keys():
                    self.print_all_metrics(**all_experiments_outcome[exp['id']])
            

    def handle_exit(self, _):
        print("Exiting emulator...")
        exit()

    def handle_help(self, _):
        self.emulator_parser.print_help()

    def handle_view(self, args):
        """
        View current settings: config, scenario, experiments
        """
        if args.setting == 'config':
            if self.emulator.config is None:
                print("No config loaded")
                return
            rprint(self.emulator.config)

        elif args.setting == 'scenario':
            if self.emulator.scenario is None:
                print("No scenario loaded")
                return
            rprint(self.emulator.scenario)
        
        elif args.setting == 'experiments':
            if self.all_experiments is None:
                print("No experiment config loaded")
                return
            rprint(self.all_experiments)

        elif args.setting == 'metrics':
            if self.all_experiments is None:
                print("No experiment config loaded")
                return
            rprint(self.all_experiments)
        
        else:
            print("Invalid option")

    @staticmethod
    def get_fields_from_string(s):
        pattern = r'(\w+)(?:\.(\w+))?'
        match = re.match(pattern, s)
        if match:
            return match.groups()
        return None

    def handle_load(self, args):
        """
        handle_load
        This function will handle the load command.
        Load experiments from a configuration file.
        This also uses the default configuration file to fill in missing fields.
        """
        if args.file is None:
            print("No file specified")
            return

        self.loaded_config = args.file
        with open(path.join('config', 'experiment_config_defaults.yml'), 'r') as default_config:
            defaults_list = yaml.safe_load(default_config)
            default_values = defaults_list[0]

        with open(path.join('config', args.file), 'r') as f:
            exp_config = yaml.safe_load(f)

        dirpattern = r'^[\w-]+$'
        filepattern = r'^[\w\.-]+$'
        required_fields = ['setup', 'setup.config', 'setup.scenario']
        id_name_fields = ['output.subdir', 'output.summary', 'output.results', 'logging.log_file']
        dir_fields = ['output.subdir']
        file_fields = ['setup.config', 'setup.scenario', 'output.summary', 'output.results', 'logging.log_file']
        bool_fields = ['flags.use_subdir', 'flags.redeploy_hosts', 'flags.redeploy_network']
        int_fields = ['trials', 'settings.max_retries', 'settings.max_errors', 'settings.max_exceptions']
        custom_fields = {
                            'logging.log_type': ['console', 'file', 'both', 'none'],
                            'logging.log_level': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            'settings.on_error': ['retry', 'skip', 'halt'],
                            'settings.on_exception': ['retry', 'skip', 'halt']
                         }
        
        unimplemented_fields = ['output.summary', 
                                'output.results', 
                                'logging.log_file',          # Note: Logging is not implemented
                                'logging.logging_type',      # Note: Logging is not implemented
                                'logging.log_level',         # Note: Logging is not implemented
                                'settings.on_error',         # Note: Retry is not implemented
                                'settings.on_exception',     # Note: Retry is not implemented 
                                'settings.max_retries',      # Note: Retry is not implemented
                                ]
        parent_names = ['setup', 'output', 'logging', 'flags', 'settings']
        all_experiment_ids = []

        for experiment in exp_config:
            defaults = copy.deepcopy(default_values)
            invalid_experiment = False

            # Check that ID exists and is valid. This ignores strict mode
            if 'id' not in experiment or not re.match(dirpattern, experiment['id']):
                print(f"{Fore.RED}Invalid experiment ID for experiment {exp_id}{Style.RESET_ALL}")
                print(f"{Fore.RED}All Experiments must have unique ID's. Aborting...{Style.RESET_ALL}")
                self.all_experiments = []
                invalid_experiment = True
                break

            exp_id = experiment['id']

            # Ensure no duplicate experiment id's. Also ignores strict mode
            if exp_id in all_experiment_ids:
                print(f"{Fore.RED}Duplicate Experiment ID {exp_id} found.{Style.RESET_ALL}")
                print(f"{Fore.RED}All Experiments must have unique ID's. Aborting...{Style.RESET_ALL}")
                self.all_experiments = []
                invalid_experiment = True
                break
            
            all_experiment_ids.append(exp_id)

            # Check that all required fields are present
            for required_field in required_fields:
                (field, subfield) = self.get_fields_from_string(required_field)    
                if field not in experiment:
                    print(f"{Fore.RED}Experiment {exp_id} missing required field: {field}{Style.RESET_ALL}")
                    invalid_experiment = True
                elif subfield is not None and subfield not in experiment[field]:
                    print(f"{Fore.RED}Experiment {exp_id} missing required subfield of field {field}: {subfield}{Style.RESET_ALL}")
                    invalid_experiment = True

            # Add default values for missing optional fields
            new_experiment = {**defaults, **experiment}
            for field in defaults.keys():
                if field not in experiment:
                    new_experiment[field] = defaults[field]
                elif type(defaults[field]) == dict:
                    for subfield in defaults[field].keys():
                        if subfield not in experiment[field]:
                            new_experiment[field][subfield] = defaults[field][subfield]



            # Find all the fields that have the default exp_id name and replace 
            # it with the experiment's id
            for id_name_field in id_name_fields:
                (field, subfield) = self.get_fields_from_string(id_name_field)
                if subfield is None and 'exp_id' in new_experiment[field]:
                    new_experiment[field] = new_experiment[field].replace('exp_id', exp_id)
                elif 'exp_id' in new_experiment[field][subfield]:
                    new_experiment[field][subfield] = new_experiment[field][subfield].replace('exp_id', exp_id)
            
            # Validate all directories to be correct directory names (alphanumeric with dashes and underscores)
            for dir_field in dir_fields:
                (field, subfield) = self.get_fields_from_string(dir_field)
                item = new_experiment[field][subfield] if subfield is not None else new_experiment[field]
                if not re.match(dirpattern, item):
                    print(f"{Fore.RED}Invalid directory name {item} for {dir_field} in experiment {exp_id}{Style.RESET_ALL}")
                    invalid_experiment = True

            # Validate all files to be correct file names (alphanumeric with dashes, underscores, and dots)
            for file_field in file_fields:
                (field, subfield) = self.get_fields_from_string(file_field)
                item = new_experiment[field][subfield] if subfield is not None else new_experiment[field]
                if not re.match(filepattern, item):
                    print(f"{Fore.RED}Invalid filename {item} for {file_field} in experiment {exp_id}{Style.RESET_ALL}")
                    invalid_experiment = True

            # Validate all boolean fields to be boolean
            for bool_field in bool_fields:
                (field, subfield) = self.get_fields_from_string(bool_field)
                item = new_experiment[field][subfield] if subfield is not None else new_experiment[field]
                if not type(item) == bool:
                    print(f"{Fore.RED}Invalid value {item} for {bool_field} in experiment {exp_id}; must be boolean{Style.RESET_ALL}")
                    invalid_experiment = True
            
            # Validate all int fields to be int
            for int_field in int_fields:
                (field, subfield) = self.get_fields_from_string(int_field)
                item = new_experiment[field][subfield] if subfield is not None else new_experiment[field]
                if not type(item) == int:
                    print(f"{Fore.RED}Invalid value {item} for {int_field} in experiment {exp_id}; must be integer{Style.RESET_ALL}")
                    invalid_experiment = True
            
            # Validate all custom fields to be valid options based on the field's options
            for custom_field in custom_fields.keys():
                (field, subfield) = self.get_fields_from_string(custom_field)
                item = new_experiment[field][subfield] if subfield is not None else new_experiment[field]
                if item not in custom_fields[custom_field]:
                    print(f"{Fore.RED}Invalid value {item} for {custom_field} in experiment {exp_id}; must be one of {custom_fields[custom_field]}{Style.RESET_ALL}")
                    invalid_experiment = True

            # If the experiment is invalid, reach based on the strict flag
            if invalid_experiment:
                if (args.strict):
                    print(f"{Fore.YELLOW}Strict mode enabled! Halting...{Style.RESET_ALL}")
                    self.all_experiments = []
                    print(f"{Fore.YELLOW}No experiments are loaded.{Style.RESET_ALL}")
                    return
                else:
                    print(f"{Fore.YELLOW}Skipping loading of experiment {exp_id} due to invalidity.{Style.RESET_ALL}")
                    continue
            

            print(f"{Fore.GREEN}Sucessfully loaded experiment {exp_id}{Style.RESET_ALL}")
            self.all_experiments.append(new_experiment)

            rprint(new_experiment)
            
        return

    
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Name of configuration file', required=False)
    parser.add_argument('-s', '--scenario', help='Name of scenario file', required=False)

    parser.add_argument('-i', '--interactive', help='Run emulator in interactive mode', action='store_true', default=False)

    parser.add_argument('-o', '--output', help='Output subdir in metrics dir', default=None)

    parser.add_argument('-r', '--redeploy-hosts', help='Re-execute all setup tasks without using snapshots', action='store_true', default=False)
    parser.add_argument('-R', '--redeploy-network', help='Redeploy network topology', action='store_true', default=False)
    
    parser.add_argument('-t', '--test', help='placeholder', action='store_true', default=False)

    parser.add_argument('-d', '--debug', help='(ALWAYS ON). debug mode', action='store_true', default=False)
    args = parser.parse_args()

    # if args.test:
    #     test_task = progress.add_task("[yellow]Running Experiment Trials", start=False, total=10)
    #     with progress:
    #         progress.start_task(test_task)
    #         for i in range(10):
    #             progress.update(test_task, refresh=True, advance=1)
    #             time.sleep(4.3)
    #     exit(0)

    print(f"Starting emulator in {'' if args.interactive else 'non-'}interactive mode...")
    
    if args.debug:
        rprint("This flag is currently inactive. Debug mode always on. Ignoring...")

    # open yml config file
    if args.config:
        with open(path.join('config', args.config), 'r') as f:
            config = yaml.safe_load(f)

    # open yml config file
    if args.scenario:
        with open(path.join('scenarios', args.scenario), 'r') as f:
            scenario = yaml.safe_load(f)

    emulator = Emulator()

    if args.output:
        emulator.set_output_subdir(args.output)

    if args.interactive:
        if args.redeploy_hosts:
            emulator.setup(config, scenario, redeploy_hosts=args.redeploy_hosts, redeploy_network=args.redeploy_network)
        
        if args.scenario:
            emulator.scenario = scenario
        if args.config:
            emulator.config = config
        EmulatorInteractive(emulator).start_interactive_emulator()

    else:
        emulator.setup(config, scenario, redeploy_hosts=args.redeploy_hosts, redeploy_network=args.redeploy_network)
        emulator.run()

        # Print metrics
        emulator.goalkeeper.print_metrics()
        emulator.attacker.cleanup()