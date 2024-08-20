from attacker import Attacker


class Haiku3(Attacker):
    def __init__(self, caldera_api_key, operation_id=None):
        name = "Haiku 3"
        strategy = "haiku3_strategy"
        super().__init__(caldera_api_key, operation_id, name, strategy)
