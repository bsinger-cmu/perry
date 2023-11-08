import os
import json
import dateutil.parser as time_parser
from collections import OrderedDict


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


def pre_process_data(data):
    process_experiment_flag_timestamps(data)
    return data


# merge subdirectories into a dictionary
def ingest_data_dir(dir_path):
    subdirectories = os.listdir(dir_path)
    data = {}
    # Go through each subdirectory and merge json files
    for subdirectory in subdirectories:
        if os.path.isdir(os.path.join(dir_path, subdirectory)):
            data[subdirectory] = merge_json_files(os.path.join(dir_path, subdirectory))

    data = pre_process_data(data)

    # Sort data by experiment name
    data = OrderedDict(sorted(data.items()))

    return data
