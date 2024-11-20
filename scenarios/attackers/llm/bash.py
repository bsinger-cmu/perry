from attacker.config.attacker_config import AbstractionLevel
from scenarios.Scenario import AttackerInformation

### Google LLMs ###
gemini1_5_pro_bash = AttackerInformation(
    name="Gemini1.5Pro_bash",
    strategy="gemini_15_pro_strategy.5Pro",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

### OpenAI LLMs ###
gpt4o_mini_bash = AttackerInformation(
    name="GPT4oMini_bash",
    strategy="gpt4o_mini_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

gpt4o_bash = AttackerInformation(
    name="GPT4o_bash",
    strategy="gpt4o_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

### Anthropic LLMs ###
haiku3_bash = AttackerInformation(
    name="Haiku3_bash",
    strategy="haiku3_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

sonnet3_bash = AttackerInformation(
    name="Sonnet3_bash",
    strategy="sonnet3_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

sonnet3_5_bash = AttackerInformation(
    name="Sonnet3.5_bash",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)
