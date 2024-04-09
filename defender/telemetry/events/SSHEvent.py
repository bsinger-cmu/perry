from .HighLevelEvent import HighLevelEvent


class SSHEvent(HighLevelEvent):

    def __init__(self, source_ip: str, target_ip: str, port: int) -> None:
        super().__init__()

        self.source_ip = source_ip
        self.target_ip = target_ip
        self.port = port
