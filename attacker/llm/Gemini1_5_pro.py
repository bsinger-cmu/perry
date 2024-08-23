from attacker import Attacker


class Gemini1_5Pro(Attacker):
    def __init__(self, caldera_api_key, operation_id=None):
        name = "Gemini 1.5 Pro"
        strategy = "gemini_15_pro_strategy"
        super().__init__(caldera_api_key, operation_id, name, strategy)
