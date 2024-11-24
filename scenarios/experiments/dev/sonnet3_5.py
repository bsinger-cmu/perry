from scenarios.attackers.llm.perry_llms import sonnet3_5_perry
from scenarios.attackers.llm.low_level import haiku3_5_low_level
from scenarios.attackers.llm.bash import haiku3_5_bash
from scenarios.attackers.llm.no_services import haiku3_5_no_services
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=sonnet3_5_perry,
            defender=absent,
            environment="DevEnvironment",
        ),
        trials=1,
    ),
]
