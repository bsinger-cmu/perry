import inspect
from rich import print

# Orchestrator actions
from defender.orchestrator.openstack_actuators import (
    StartHoneyService,
    DeployDecoy,
    AddHoneyCredentials,
)

# Telemetry
from defender.telemetry import TelemetryAnalysis, SimpleTelemetryAnalysis

# Strategy
from defender.strategy import StaticRandom, WaitAndStop
from defender.strategy.setup import RandomPlacement


def get_function_semantic_lines(functions):
    if not isinstance(functions, list):
        functions = [functions]

    semantic_lines = []
    for func in functions:
        lines = inspect.getsourcelines(func)
        semantic_lines += get_semantic_lines(lines[0])

    return semantic_lines


def get_semantic_lines(lines):
    semantic_lines = []
    for line in lines:
        if line.strip().startswith("#"):
            continue
        if "log_event" in line.strip():
            continue
        if line.strip() == "":
            continue
        if line.strip() == "\n":
            continue

        semantic_lines.append(line)
    return semantic_lines


def get_ansible_semantic_lines(filepath: str):
    with open(filepath, "r") as f:
        lines = f.readlines()
        semantic_lines = get_semantic_lines(lines)
        return semantic_lines


def count_low_level_action_lines(low_level_action):
    lines = 0
    for function in low_level_action:
        # if function is string
        if isinstance(function, str):
            lines += len(get_ansible_semantic_lines(function))
        else:
            lines += len(get_function_semantic_lines(function))

    return lines


def count_strategy_lines_without_perry(
    strategy, low_level_action_lines, telemetry_lines
):
    lines = 0
    for function in strategy:
        for line in get_function_semantic_lines(function):
            # If line is a call to a low level action
            line_is_low_level_action = False
            for action, action_lines in low_level_action_lines.items():
                if action in line:
                    lines += action_lines
                    line_is_low_level_action = True
                    break

            if not line_is_low_level_action:
                lines += 1

    lines += telemetry_lines
    return lines


if __name__ == "__main__":
    low_level_actions = {
        "StartHoneyService": [
            StartHoneyService.actuate,
            "ansible/defender/deploy_honey_service.yml",
        ],
        # Deploy decoy uses StartHoneyService
        "DeployDecoy": [
            DeployDecoy.actuate,
            "ansible/defender/deploy_honey_service.yml",
            StartHoneyService.actuate,
        ],
        "AddHoneyCredentials": [
            AddHoneyCredentials.actuate,
            "ansible/common/createUser/createUser.yml",
            "ansible/deployment_instance/setup_server_ssh_keys/setup_server_ssh_keys.yml",
        ],
    }

    telemetry = {
        "SimpleTelemetryAnalysis": [
            TelemetryAnalysis.get_new_telemetry,
            SimpleTelemetryAnalysis.process_low_level_events,
        ],
    }

    strategies = {
        "StaticRandom": [
            StaticRandom.initialize,
            RandomPlacement.randomly_place_deception,
            StaticRandom.run,
        ],
        "WaitAndStop": [
            WaitAndStop.initialize,
            RandomPlacement.randomly_place_deception,
            WaitAndStop.run,
        ],
    }

    # Count low level action lines
    low_level_action_lines = {}
    for action, details in low_level_actions.items():
        low_level_action_lines[action] = count_low_level_action_lines(details)

    # Count telemetry lines
    telemetry_lines = {}
    for analysis, details in telemetry.items():
        telemetry_lines[analysis] = count_low_level_action_lines(details)

    # Count strategy lines
    strategy_lines = {}
    for strategy, details in strategies.items():
        strategy_lines[strategy] = count_low_level_action_lines(details)

    # Count strategy lines without Perry
    strategy_lines_without_perry = {}
    strategy_lines_without_perry["StaticRandom"] = count_strategy_lines_without_perry(
        strategies["StaticRandom"],
        low_level_action_lines,
        telemetry_lines["SimpleTelemetryAnalysis"],
    )

    strategy_lines_without_perry["WaitAndStop"] = count_strategy_lines_without_perry(
        strategies["WaitAndStop"],
        low_level_action_lines,
        telemetry_lines["SimpleTelemetryAnalysis"],
    )

    print(low_level_action_lines)
    print(telemetry_lines)
    print(strategy_lines)
    print(strategy_lines_without_perry)
