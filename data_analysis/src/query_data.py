import pandas as pd
from statistics import mean

from deployment_instance import ExperimentResult, FlagInformation, DataExfiltrated


def get_flags_captured(data: list[ExperimentResult]):
    flags_data: list[list[FlagInformation]] = []

    for experiment in data:
        flags_data.append(experiment.flags_captured)

    return flags_data


def get_data_exfiltrated(data: list[ExperimentResult]):
    data_exfiltrated: list[list[DataExfiltrated]] = []

    for experiment in data:
        data_exfiltrated.append(experiment.data_exfiltrated)

    return data_exfiltrated


def get_data_exfiltration_times(
    data: list[ExperimentResult],
    convert_to_minutes: bool = True,
    expected_files: int = 2,
):
    data_exfiltrated = get_data_exfiltrated(data)
    time_exiltrated_all_data = []

    for experiment_result in data_exfiltrated:
        data_exfiltration_times = []
        for data_exfiltrated in experiment_result:
            if convert_to_minutes:
                data_exfiltration_times.append(data_exfiltrated.time_exfiltrated / 60)
            else:
                data_exfiltration_times.append(data_exfiltrated.time_exfiltrated)

        if len(data_exfiltration_times) == 0:
            continue

        if len(data_exfiltration_times) >= expected_files:
            time_exiltrated_all_data.append(max(data_exfiltration_times))

    return time_exiltrated_all_data


def percent_of_data_exfiltrated(data: list[ExperimentResult], expected_files: int = 2):
    data_exfiltrated = get_data_exfiltrated(data)
    percent_exfiltrated_all_data = []

    for experiment_result in data_exfiltrated:
        percent_exfiltrated_all_data.append(len(experiment_result) / expected_files)

    return mean(percent_exfiltrated_all_data) * 100


# For each experiment get runtime data
def get_runtime_data(experiment_data):
    runtime_data = {}

    for experiment_type in experiment_data.keys():
        runtime_data[experiment_type] = []
        experiment_type_data = experiment_data[experiment_type]
        for experiment in experiment_type_data:
            # Convert data to minutes
            experiment["execution_time"] = (experiment["execution_time"]) / 60
            runtime_data[experiment_type].append(experiment["execution_time"])

    return runtime_data


# Sort flags by created_on timestamp
def sort_flags_by_timestamp(flags):
    return sorted(flags, key=lambda k: k["time_taken"])


def get_experiment_flag_time_taken(experiment_data, flag_num):
    data = []
    for experiment in experiment_data:
        if len(experiment["flags_captured"]) < flag_num:
            continue
        # Sort flags by time_taken
        experiment["flags"] = sort_flags_by_timestamp(experiment["flags_captured"])
        # Get time_taken for flag_num
        flag = experiment["flags"][flag_num - 1]
        # Convert time_taken to minutes
        time_taken = flag["time_taken"] / 60
        data.append(time_taken)
    return data


def get_flag_time_taken(experiment_data, flag_nums):
    data = {}
    for experiment_type in experiment_data.keys():
        data[experiment_type] = {}

        if isinstance(flag_nums, list):
            for flag_num in flag_nums:
                data[experiment_type][flag_num] = get_experiment_flag_time_taken(
                    experiment_data[experiment_type], flag_num
                )
        else:
            data[experiment_type] = get_experiment_flag_time_taken(
                experiment_data[experiment_type], flag_nums
            )
    return data


def get_avg_flag_time_taken(experiment_data, flag_nums):
    data = {}
    for experiment_type in experiment_data.keys():
        data[experiment_type] = []
        for flag_num in flag_nums:
            time_taken_flags = get_experiment_flag_time_taken(
                experiment_data[experiment_type], flag_num
            )

            if len(time_taken_flags) != 0:
                data[experiment_type].append(mean(time_taken_flags))
    return data


def get_flag_time_taken_pd(experiment_data, flag_num):
    data = pd.DataFrame()
    for experiment_type in experiment_data.keys():
        times_for_flag = get_experiment_flag_time_taken(
            experiment_data[experiment_type], flag_num
        )

        data = pd.concat(
            [data, pd.DataFrame(times_for_flag, columns=[experiment_type])], axis=1
        )
    # Flags start at 1 not 0
    data.index += 1

    return data
