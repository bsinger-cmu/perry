from attacker import Attacker


class Sonnet3_5(Attacker):
    def __init__(self, caldera_api_key, operation_id=None):
        name = "Sonnet 3.5"
        strategy = "sonnet3_5_strategy"
        super().__init__(caldera_api_key, operation_id, name, strategy)
