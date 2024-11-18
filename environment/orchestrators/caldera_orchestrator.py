from .orchestrator import Orchestrator, OrcehstratorTask


# Caldera Orchestrator
class CalderaOrchestrator(Orchestrator):
    def __init__(self, ansible_runner) -> None:
        super().__init__(ansible_runner, "caldera/")

    def install_attacker(self, host: str, user: str, caldera_ip: str):
        task = OrcehstratorTask(host, "install_attacker")
        task.set_params({"user": user, "caldera_ip": caldera_ip})
        self.add_task(task)

    def install_defender(self, host: str, user: str, caldera_ip: str):
        task = OrcehstratorTask(host, "install_defender")
        task.set_params({"user": user, "caldera_ip": caldera_ip})
        self.add_task(task)
