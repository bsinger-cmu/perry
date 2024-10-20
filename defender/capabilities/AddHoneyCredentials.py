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
        fakeData: bool = True,
        honey_user: str | None = None,
    ):
        self.credential_host = credential_host
        self.honey_host = honey_host
        self.number = number
        self.real = real
        self.fakeData = fakeData
        self.honey_user = honey_user
