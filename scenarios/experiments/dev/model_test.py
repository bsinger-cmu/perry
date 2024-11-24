from scenarios.attackers.llm.perry_llms import (
    haiku3_5_perry,
    gemini1_5_flash_perry,
    gpt4o_mini_perry,
)
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=gemini1_5_flash_perry,
            defender=absent,
            environment="DevEnvironment",
        ),
        trials=1,
    ),
    Experiment(
        scenario=Scenario(
            attacker=gpt4o_mini_perry,
            defender=absent,
            environment="DevEnvironment",
        ),
        trials=1,
    ),
    Experiment(
        scenario=Scenario(
            attacker=haiku3_5_perry,
            defender=absent,
            environment="DevEnvironment",
        ),
        trials=0,
    ),
]
