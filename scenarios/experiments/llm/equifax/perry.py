from scenarios.attackers.llm.perry_llms import haiku3_perry
from scenarios.defenders.absent import absent
from scenarios.Scenario import Scenario, Experiment

experiment = [
    Experiment(
        scenario=Scenario(
            attacker=haiku3_perry,
            defender=absent,
            environment="EquifaxLarge",
        ),
        trials=1,
    )
]
