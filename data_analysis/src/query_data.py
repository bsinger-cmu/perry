import pandas as pd
from statistics import mean

from deployment_instance.Result import (
    ExperimentResult,
    DataExfiltrated,
)


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

            if len(data_exfiltration_times) == 0:
                time_exfiltrated_per_file.append(0)
            else:
                time_exfiltrated_per_file.append(
                    exfiltration_time / len(data_exfiltration_times)
                )
        else:
            time_exiltrated_all_data.append(timeout_time_min)
            survival_data.append(0)
            if len(data_exfiltration_times) == 0:
                time_exfiltrated_per_file.append(0)
            else:
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


def total_control_host_capture_times(
    data: dict[str, ExperimentResult], experiment_name: str
):
    critical_hosts = [
        "control-host-0",
        "control-host-1",
        "control-host-2",
        "control-host-3",
        "control-host-4",
    ]
    df = pd.DataFrame(
        columns=[
            "experiment_name",
            "experiment_id",
            "avg_time_infected",
            "percent_hosts_infected",
        ]
    )

    for exp_id, result in data.items():
        capture_times = []
        for host in result.hosts_infected:
            if host.name in critical_hosts:
                capture_times.append(host.time_infected)

        # Calculate the number and average time of infected hosts
        infected_count = len(capture_times)
        percent_hosts_infected = (infected_count / len(critical_hosts)) * 100

        if infected_count > 0:
            avg_time_infected = (
                sum(capture_times) / infected_count / 60
            )  # Convert to minutes
        else:
            avg_time_infected = None  # or use 0 if you prefer

        # Append row to the dataframe
        df.loc[df.shape[0]] = [
            experiment_name,
            exp_id,
            avg_time_infected,
            percent_hosts_infected,
        ]

    return df


critical_hosts = [
    "control-host-0",
    "control-host-1",
    "control-host-2",
    "control-host-3",
    "control-host-4",
]


def total_control_host_capture_times(
    data: dict[str, ExperimentResult], num_expected_files
):
    df = pd.DataFrame(
        columns=[
            "experiment",
            "experiment_num",
            "hosts_infected",
            "percent_hosts_infected",
            "time_per_host",
        ]
    )

    for experiment_num, experiment_result in enumerate(list(data.values())):
        hosts_infected = get_num_critical_hosts_infected(experiment_result)
        avg_time_infected = get_avg_time_infected(experiment_result)
        if avg_time_infected is not None:
            avg_time_infected = avg_time_infected / 60

        df.loc[df.shape[0]] = [
            experiment_result.scenario.name,
            experiment_num,
            hosts_infected,
            hosts_infected / len(critical_hosts) * 100,
            avg_time_infected,
        ]

    return df


def get_num_critical_hosts_infected(exp: ExperimentResult):
    infected_hosts = [host.name for host in exp.hosts_infected]
    num_critical_hosts_infected = len(set(critical_hosts).intersection(infected_hosts))
    return num_critical_hosts_infected


def get_avg_time_infected(exp: ExperimentResult):
    infected_hosts = [host.name for host in exp.hosts_infected]
    critical_host_times = []
    for host in exp.hosts_infected:
        if host.name in critical_hosts:
            critical_host_times.append(host.time_infected)
    if len(critical_host_times) > 0:
        avg_time_infected = sum(critical_host_times) / len(critical_host_times)
    else:
        avg_time_infected = None
    return avg_time_infected
