from attacker import Attacker


class Opus3(Attacker):
    def __init__(self, caldera_api_key, operation_id=None):
        name = "Opus 3"
        strategy = "opus3_strategy"
        super().__init__(caldera_api_key, operation_id, name, strategy)
