from . import Action
from deployment_instance.network import Host


class AddHoneyCredentials(Action):
    name = "AddHoneyCredentials"

    def __init__(
        self,
        credential_host: Host,
        honey_host: Host,
        number: int = 1,
        real: bool = True,
    ):
        self.credential_host = credential_host
        self.honey_host = honey_host
        self.number = number
        self.real = real
