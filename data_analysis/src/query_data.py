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
    data: dict[str, ExperimentResult],
    convert_to_minutes: bool = True,
    expected_files: int = 2,
    timeout_time_min: int = 60,
):
    data_exfiltrated = get_data_exfiltrated(list(data.values()))
    time_exiltrated_all_data = []
    time_exfiltrated_per_file = []
    survival_data = []
    num_files = []
    experiment_ids = []

    for experiment_id, experiment_result in data.items():
        data_exfiltration_times = []
        experiment_ids.append(experiment_id)
        for idx, data_exfiltrated in enumerate(experiment_result.data_exfiltrated):
            if convert_to_minutes:
                time_min = data_exfiltrated.time_exfiltrated / 60
                data_exfiltration_times.append(time_min)
            else:
                data_exfiltration_times.append(data_exfiltrated.time_exfiltrated)

        num_files.append(len(data_exfiltration_times))
        if len(data_exfiltration_times) >= expected_files:
            # Sort data exfiltration times in ascending order
            data_exfiltration_times.sort()
            exfiltration_time = data_exfiltration_times[expected_files - 1]
            time_exiltrated_all_data.append(exfiltration_time)
            survival_data.append(1)
            time_exfiltrated_per_file.append(
                exfiltration_time / len(data_exfiltration_times)
            )
        else:
            time_exiltrated_all_data.append(timeout_time_min)
            survival_data.append(0)
            time_exfiltrated_per_file.append(
                timeout_time_min / len(data_exfiltration_times)
            )

    df_data = {
        "time_exfiltrated": time_exiltrated_all_data,
        "time_exfiltrated_per_file": time_exfiltrated_per_file,
        "survival": survival_data,
        "num_files": num_files,
        "experiment_id": experiment_ids,
    }
    df = pd.DataFrame(df_data)
    return df


def get_exfiltration_time_df(data: dict[str, ExperimentResult], num_expected_files):
    df = pd.DataFrame(
        columns=[
            "experiment",
            "experiment_num",
            "time_exfiltrated",
            "time_per_file",
            "files_exfiltrated",
            "percent_files_exfiltrated",
        ]
    )

    for experiment_num, experiment_result in enumerate(list(data.values())):
        if len(experiment_result.data_exfiltrated) == 0:
            df.loc[df.shape[0]] = [
                experiment_result.scenario.name,
                experiment_num,
                0,
                0,
                0,
                0,
            ]
            continue

        files_exfiltrated = len(experiment_result.data_exfiltrated)
        time_exfiltrated = experiment_result.data_exfiltrated[-1].time_exfiltrated
        time_per_file = time_exfiltrated / files_exfiltrated
        percent_files = files_exfiltrated / num_expected_files

        df.loc[df.shape[0]] = [
            experiment_result.scenario.name,
            experiment_num,
            time_exfiltrated / 60,
            time_per_file / 60,
            files_exfiltrated,
            percent_files * 100,
        ]

    return df


def get_data_exfiltration_cdf(data: dict[str, ExperimentResult], num_expected_files):
    df = pd.DataFrame(
        columns=[
            "experiment",
            "experiment_num",
            "time_exfiltrated",
            "file_number",
            "percent_data",
        ]
    )

    for experiment_num, experiment_result in enumerate(list(data.values())):
        for idx, data_exfiltrated in enumerate(experiment_result.data_exfiltrated):
            df.loc[df.shape[0]] = [
                experiment_result.scenario.name,
                experiment_num,
                data_exfiltrated.time_exfiltrated / 60,
                idx + 1,
                ((idx + 1) / num_expected_files) * 100,
            ]

    return df


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
