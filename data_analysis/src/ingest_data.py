import os
import json
import dateutil.parser as time_parser
from collections import OrderedDict
from environment import ExperimentResult


# merge json files in a directory into one object
def merge_json_files(dir_path):
    dir_contents = os.listdir(dir_path)
    data = []

    # To be backwords comptabile with old data
    if "metrics" in dir_contents:
        dir_path = os.path.join(dir_path, "metrics")
        dir_contents = os.listdir(dir_path)

    for file in dir_contents:
        if file.endswith(".json") and file.startswith("metrics"):
            with open(os.path.join(dir_path, file), "r") as f:
                data.append(json.load(f))

    return data


def process_experiment_flag_timestamps(data):
    for experiment_type in data.keys():
        experiment_type_data = data[experiment_type]
        for experiment in experiment_type_data:
            experiment_start_time = experiment["start_time"]
            experiment_flags = experiment["flags_captured"]
            for flag in experiment_flags:
                # Parse created_by timestamp
                str_timestamp = flag["created_on"]
                # Example timestap 2023-10-02T20:55:08Z
                flag_time = time_parser.parse(str_timestamp)

                flag["created_on_timestamp"] = flag_time.timestamp()
                flag["time_taken"] = flag_time.timestamp() - experiment_start_time
                flag["experiment_starttime"] = experiment_start_time


def pre_process_data(data: dict[str, ExperimentResult]):
    # filter duplicate data exfiltrations
    for experiment_type, experiment_data in data.items():
        files_exfiltrated = []
        for exfiltrated_data in experiment_data.data_exfiltrated:
            # Get file name before the extension
            file_name_parts = exfiltrated_data.name.split(".")
            file_name = file_name_parts[0]
            if file_name not in files_exfiltrated:
                files_exfiltrated.append(file_name)
            else:
                experiment_data.data_exfiltrated.remove(exfiltrated_data)

    return data


# Load experiment results from a directory
def ingest_experiment_results(dir_path):
    subdirectories = os.listdir(dir_path)
    experiment_results: dict[str, ExperimentResult] = {}
    # experiment_results: dict[ExperimentResult] = []

    for execution_dir in subdirectories:
        if os.path.isdir(os.path.join(dir_path, execution_dir)):
            result_file = os.path.join(dir_path, execution_dir, "result.json")
            with open(result_file, "r") as f:
                experiment_results[execution_dir] = ExperimentResult(**json.load(f))

    experiment_results = pre_process_data(experiment_results)

    return experiment_results


# merge subdirectories into a dictionary
def ingest_data_dir(dir_path):
    subdirectories = os.listdir(dir_path)
    data = {}

    # Go through each subdirectory and merge json files
    for subdirectory in subdirectories:
        if os.path.isdir(os.path.join(dir_path, subdirectory)):
            data[subdirectory] = ingest_experiment_results(
                os.path.join(dir_path, subdirectory)
            )

    return data
