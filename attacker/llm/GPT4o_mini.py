from attacker import Attacker


class GPT4oMini(Attacker):
    def __init__(self, caldera_api_key, operation_id=None):
        name = "GPT 4o Mini"
        strategy = "gpt4o_mini_strategy"
        super().__init__(caldera_api_key, operation_id, name, strategy)
