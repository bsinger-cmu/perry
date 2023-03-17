from .HighLevelEvent import HighLevelEvent

class AttackerOnHost(HighLevelEvent):

    def __init__(self, attacker_ip) -> None:
        super().__init__()
        
        self.attacker_ip = attacker_ip