from .HighLevelEvent import HighLevelEvent


class DecoyCredentialUsed(HighLevelEvent):

    def __init__(self, source_ip: str, decoy_user: str) -> None:
        super().__init__()

        self.source_ip = source_ip
        self.decoy_user = decoy_user
