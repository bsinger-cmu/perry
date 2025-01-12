import pandas as pd
from statistics import mean

from environment.Result import (
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


TIMEOUT = 75 * 60


def get_exfiltration_time_df(
    data: dict[str, ExperimentResult], num_expected_files, defender_name="defender"
):
    df = pd.DataFrame(
        columns=[
            "experiment",
            "operation_id",
            "defender",
            "attacker",
            "experiment_num",
            "time_exfiltrated",
            "time_per_file",
            "files_exfiltrated",
            "percent_files_exfiltrated",
            "execution_time",
            "experiment_time",
            "setup_time",
        ]
    )

    defender_attacker_count = {}

    for experiment_num, experiment_result in enumerate(list(data.values())):
        if experiment_result.scenario.attacker.name not in defender_attacker_count:
            defender_attacker_count[experiment_result.scenario.attacker.name] = 0
        defender_attacker_count[experiment_result.scenario.attacker.name] += 1

        if len(experiment_result.data_exfiltrated) == 0:
            df.loc[df.shape[0]] = [
                experiment_result.scenario.name,
                experiment_result.operation_id,
                defender_name,
                experiment_result.scenario.attacker.name,
                defender_attacker_count[experiment_result.scenario.attacker.name],
                TIMEOUT / 60,
                0,
                0,
                0,
                experiment_result.execution_time / 60,
                experiment_result.experiment_time / 60,
                experiment_result.setup_time / 60,
            ]
            continue

        files_exfiltrated = len(experiment_result.data_exfiltrated)
        if files_exfiltrated < num_expected_files - 5:
            time_exfiltrated = TIMEOUT
        else:
            time_exfiltrated = experiment_result.data_exfiltrated[-1].time_exfiltrated

        time_per_file = time_exfiltrated / files_exfiltrated
        percent_files = files_exfiltrated / num_expected_files

        df.loc[df.shape[0]] = [
            experiment_result.scenario.name,
            experiment_result.operation_id,
            defender_name,
            experiment_result.scenario.attacker.name,
            defender_attacker_count[experiment_result.scenario.attacker.name],
            time_exfiltrated / 60,
            time_per_file / 60,
            files_exfiltrated,
            percent_files * 100,
            experiment_result.execution_time / 60,
            experiment_result.experiment_time / 60,
            experiment_result.setup_time / 60,
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


critical_hosts = [
    "control-host-0",
    "control-host-1",
    "control-host-2",
    "control-host-3",
    "control-host-4",
]
ICS_TIMEOUT = 24 * 60


def total_control_host_capture_times(
    data: dict[str, ExperimentResult],
    defender="defender",
):
    df = pd.DataFrame(
        columns=[
            "experiment",
            "operation_id",
            "defender",
            "attacker",
            "experiment_num",
            "hosts_infected",
            "percent_hosts_infected",
            "time_taken",
            "time_per_host",
            "execution_time",
        ]
    )
    defender_attacker_count = {}

    for experiment_num, experiment_result in enumerate(list(data.values())):
        if experiment_result.scenario.attacker.name not in defender_attacker_count:
            defender_attacker_count[experiment_result.scenario.attacker.name] = 0
        defender_attacker_count[experiment_result.scenario.attacker.name] += 1

        hosts_infected = get_num_critical_hosts_infected(experiment_result)
        avg_time_infected = get_avg_time_infected(experiment_result)
        if hosts_infected != len(critical_hosts):
            time_taken = ICS_TIMEOUT / 60
        else:
            time_taken = get_time_of_last_critical(experiment_result) / 60

        df.loc[df.shape[0]] = [
            experiment_result.scenario.name,
            experiment_result.operation_id,
            defender,
            experiment_result.scenario.attacker.name,
            defender_attacker_count[experiment_result.scenario.attacker.name],
            hosts_infected,
            hosts_infected / len(critical_hosts) * 100,
            time_taken,
            avg_time_infected,
            experiment_result.execution_time / 60,
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


def get_time_of_last_critical(exp: ExperimentResult):
    critical_host_times = []
    for host in exp.hosts_infected:
        if host.name in critical_hosts:
            critical_host_times.append(host.time_infected)
    if len(critical_host_times) > 0:
        last_time_infected = max(critical_host_times)
    else:
        last_time_infected = 0
    return last_time_infected
