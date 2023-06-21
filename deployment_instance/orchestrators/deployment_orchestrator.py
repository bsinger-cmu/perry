from .orchestrator import Orchestrator, OrchestrationTask

    
# Deployment Orchestrator
class DeploymentOrchestrator(Orchestrator):
    def __init__(self, ansible_runner) -> None:
        super().__init__(ansible_runner, "deployment_instance/")

    def check_host_liveness(self, host: str):
        self.add_task(OrchestrationTask(host, "check_if_host_up"))

    def install_base_packages(self, host: str):
        self.add_task(OrchestrationTask(host, "install_base_packages"))
    