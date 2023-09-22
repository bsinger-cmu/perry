import os
import json


# merge json files in a directory into one object
def merge_json_files(dir_path):
    files = os.listdir(dir_path)
    data = []
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(dir_path, file), "r") as f:
                data.append(json.load(f))

    return data


# merge subdirectories into a dictionary
def ingest_data_dir(dir_path):
    subdirectories = os.listdir(dir_path)
    data = {}
    for subdirectory in subdirectories:
        if os.path.isdir(os.path.join(dir_path, subdirectory)):
            data[subdirectory] = merge_json_files(os.path.join(dir_path, subdirectory))

    return data
