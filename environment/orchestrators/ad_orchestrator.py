from .orchestrator import Orchestrator, OrcehstratorTask
import yaml


# Active Directory Orchestrator
class ADOrchestrator(Orchestrator):
    def __init__(self, ansible_runner) -> None:
        super().__init__(ansible_runner, "enterprise/")

    def samba_AD(
        self, host: str, samba_workgroup: str, samba_realm: str, realm_password: str
    ):
        task = OrcehstratorTask(host, "samba-AD")
        task.set_params(
            {
                "samba_workgroup": samba_workgroup,
                "samba_realm": samba_realm,
                "realm_password": realm_password,
            }
        )
        self.add_task(task)

    def add_Groups(self, host: str):
        task = OrcehstratorTask(host, "addGroups")
        self.add_task(task)

    def add_Users(self, host: str, user_details_file: str):
        with open(user_details_file, "r") as file:
            user_details = yaml.safe_load(file)

        task = OrcehstratorTask(host, "addUsers")
        task.set_params({"user_details": user_details})
        self.add_task(task)

    def join_AD(self, host: str):
        task = OrcehstratorTask(host, "join-AD")
        self.add_task(task)
