from attacker import Attacker


class GPT3_5(Attacker):
    def __init__(self, caldera_api_key, operation_id=None):
        name = "GPT 3.5"
        strategy = "gpt3_5_strategy"
        super().__init__(caldera_api_key, operation_id, name, strategy)
