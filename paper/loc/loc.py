from rich import print

# Orchestrator actions
from defender.orchestrator.openstack_actuators import (
    StartHoneyService,
    DeployDecoy,
    AddHoneyCredentials,
    RestoreServer,
)
from openstack_helper_functions.server_helpers import find_server_by_ip

# Telemetry
from defender.telemetry import TelemetryAnalysis, SimpleTelemetryAnalysis

# Symbolic reasoning
from deployment_instance.network import Network, Subnet, Host
from deployment_instance.openstack.openstack_processor import get_hosts_on_subnet
from deployment_instance.EquifaxInstance import EquifaxInstance

# Strategy
from defender.strategy.NaiveDecoyHost import NaiveDecoyHost
from defender.strategy.NaiveDecoyCredential import NaiveDecoyCredential
from defender.strategy.StaticStandalone import StaticStandalone
from defender.strategy.StaticLayered import StaticLayered
from defender.strategy.ReactiveLayered import ReactiveLayered
from defender.strategy import ReactiveStandalone

from paper.loc.helpers import get_function_semantic_lines, count_low_level_action_lines


def count_strategy_lines_without_perry(
    strategy,
    low_level_action_lines,
    telemetry_lines,
    symbolic_reasoning_lines,
    symbolic_reasoning_lines_total,
):
    total_lines = telemetry_lines + symbolic_reasoning_lines_total
    lines_from_actions = 0
    lines_from_telemetry = telemetry_lines
    lines_from_symbolic_reasoning = symbolic_reasoning_lines_total

    for function in strategy:
        for line in get_function_semantic_lines(function):
            # If line is a call to a low level action
            skip_line = False
            for action, action_lines in low_level_action_lines.items():
                if action in line:
                    total_lines += action_lines
                    lines_from_actions += action_lines
                    skip_line = True
                    break
            for action, action_lines in symbolic_reasoning_lines.items():
                if action in line:
                    total_lines += action_lines
                    lines_from_symbolic_reasoning += action_lines
                    skip_line = True
                    break

            if not skip_line:
                total_lines += 1

    return {
        "total_lines": total_lines,
        "lines_from_actions": lines_from_actions,
        "lines_from_telemetry": lines_from_telemetry,
        "lines_from_symbolic_reasoning": lines_from_symbolic_reasoning,
    }


def semantic_line_diff(a, b):
    a = get_function_semantic_lines(a)
    b = get_function_semantic_lines(b)

    deletions = set(a) - set(b)
    additions = set(b) - set(a)

    return additions, deletions


if __name__ == "__main__":
    low_level_actions = {
        "StartHoneyService(": [
            StartHoneyService.actuate,
            "ansible/defender/deploy_honey_service.yml",
        ],
        # Deploy decoy uses StartHoneyService
        "DeployDecoy(": [
            DeployDecoy.actuate,
            "ansible/defender/deploy_honey_service.yml",
            StartHoneyService.actuate,
        ],
        "AddHoneyCredentials(": [
            AddHoneyCredentials.actuateMany,
            AddHoneyCredentials.getAnsibleActions,
            "ansible/common/createUser/createUser.yml",
            "ansible/deployment_instance/setup_server_ssh_keys/setup_server_ssh_keys.yml",
            "ansible/deployment_instance/setup_server_ssh_keys/add_to_ssh_config.yml",
        ],
        "RestoreServer(": [RestoreServer.actuate, find_server_by_ip],
    }

    symbolic_reasoning_module = [Network, Subnet, Host]
    symbolic_reasoning_functions = {
        "subnet.get_random_host()": Subnet.get_random_host,
        "network.get_random_host()": Network.get_random_host,
        "network.get_subnet_by_name(": Network.get_subnet_by_name,
        "network.get_random_subnet()": Network.get_random_subnet,
        ".add_host(": Subnet.add_host,
        " Host(": Host.__init__,
        " Subnet(": Subnet.__init__,
        " Network(": Network.__init__,
        "get_hosts_on_subnet(": get_hosts_on_subnet,
    }

    telemetry = {
        "SimpleTelemetryAnalysis": [
            TelemetryAnalysis.get_new_telemetry,
            SimpleTelemetryAnalysis.process_low_level_events,
        ],
    }

    strategies = {
        "NaiveDecoyHost": [NaiveDecoyHost],
        "NaiveDecoyCredential": [NaiveDecoyCredential],
        "StaticStandalone": [StaticStandalone],
        "StaticLayered": [StaticLayered],
        "ReactiveLayered": [ReactiveLayered],
        "ReactiveStandalone": [ReactiveStandalone],
    }
    ## Hack
    # To get telemetry linesm, add "ReactiveStandalone": [ReactiveStandalone, EquifaxInstance.parse_network],

    # Count low level action lines
    low_level_action_lines = {}
    for action, details in low_level_actions.items():
        low_level_action_lines[action] = count_low_level_action_lines(details)

    symbolic_reasoning_module_lines = {}
    for module, functions in symbolic_reasoning_functions.items():
        symbolic_reasoning_module_lines[module] = len(
            get_function_semantic_lines([functions])
        )

    # Count telemetry lines
    telemetry_lines = {}
    for analysis, details in telemetry.items():
        telemetry_lines[analysis] = count_low_level_action_lines(details)

    # Count symbolic reasoning module lines
    symbolic_reasoning_module_total_lines = 0
    for module in symbolic_reasoning_module:
        symbolic_reasoning_module_total_lines += len(
            get_function_semantic_lines(module)
        )

    # Count strategy lines
    strategy_lines = {}
    for strategy, details in strategies.items():
        strategy_lines[strategy] = count_low_level_action_lines(details)

    # Count strategy lines without Perry
    strategy_lines_without_perry = {}

    strategy_lines_without_perry["NaiveDecoyHost"] = count_strategy_lines_without_perry(
        strategies["NaiveDecoyHost"],
        low_level_action_lines,
        0,
        symbolic_reasoning_module_lines,
        symbolic_reasoning_module_total_lines,
    )

    strategy_lines_without_perry["NaiveDecoyCredential"] = (
        count_strategy_lines_without_perry(
            strategies["NaiveDecoyCredential"],
            low_level_action_lines,
            0,
            symbolic_reasoning_module_lines,
            symbolic_reasoning_module_total_lines,
        )
    )

    strategy_lines_without_perry["StaticStandalone"] = (
        count_strategy_lines_without_perry(
            strategies["StaticStandalone"],
            low_level_action_lines,
            0,
            symbolic_reasoning_module_lines,
            symbolic_reasoning_module_total_lines,
        )
    )

    strategy_lines_without_perry["StaticLayered"] = count_strategy_lines_without_perry(
        strategies["StaticLayered"],
        low_level_action_lines,
        0,
        symbolic_reasoning_module_lines,
        symbolic_reasoning_module_total_lines,
    )

    strategy_lines_without_perry["ReactiveLayered"] = (
        count_strategy_lines_without_perry(
            strategies["ReactiveLayered"],
            low_level_action_lines,
            0,
            symbolic_reasoning_module_lines,
            symbolic_reasoning_module_total_lines,
        )
    )

    strategy_lines_without_perry["ReactiveStandalone"] = (
        count_strategy_lines_without_perry(
            strategies["ReactiveStandalone"],
            low_level_action_lines,
            0,
            symbolic_reasoning_module_lines,
            symbolic_reasoning_module_total_lines,
        )
    )

    print(low_level_action_lines)
    print(telemetry_lines)
    print(strategy_lines)
    print(strategy_lines_without_perry)

    print("NaiveDecoyHost vs NaiveDecoyCredential")
    additions, deletions = semantic_line_diff([NaiveDecoyHost], [NaiveDecoyCredential])
    print("+", len(additions), "-", len(deletions))

    print("NaiveDecoyHost vs StaticStandalone")
    additions, deletions = semantic_line_diff(
        [NaiveDecoyCredential], [StaticStandalone]
    )
    print("+", len(additions), "-", len(deletions))

    print("StaticStandalone vs StaticLayered")
    additions, deletions = semantic_line_diff([StaticStandalone], [StaticLayered])
    print("+", len(additions), "-", len(deletions))

    print("StaticLayered vs ReactiveLayered")
    additions, deletions = semantic_line_diff([StaticLayered], [ReactiveLayered])
    print("+", len(additions), "-", len(deletions))
