from .orchestrator import Orchestrator, OrcehstratorTask


# Defender Orchestrator
class DefenderOrchestrator(Orchestrator):
    def __init__(self, ansible_runner) -> None:
        super().__init__(ansible_runner, "defender/")

    def install_sysflow(self, host: str):
        self.add_task(OrcehstratorTask(host, "sysflow/install_sysflow"))

    def start_sysflow(self, host: str):
        self.add_task(OrcehstratorTask(host, "sysflow/start_sysflow"))

    def deploy_honeySSH(
        self, host: str, elasticsearch_server: str, elasticsearch_api_key: str
    ):
        task = OrcehstratorTask(host, "deploy_honey_ssh")
        task.set_params(
            {
                "elasticsearch_server": elasticsearch_server,
                "elasticsearch_api_key": elasticsearch_api_key,
            }
        )
        self.add_task(task)
