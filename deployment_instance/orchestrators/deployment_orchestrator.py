from .orchestrator import Orchestrator, OrcehstratorTask


# Deployment Orchestrator
class DeploymentOrchestrator(Orchestrator):
    def __init__(self, ansible_runner) -> None:
        super().__init__(ansible_runner, "deployment_instance/")

    def check_host_liveness(self, host: str):
        self.add_task(OrcehstratorTask(host, "check_if_host_up"))

    def install_base_packages(self, host: str):
        self.add_task(OrcehstratorTask(host, "install_base_packages"))

    def setup_server_ssh_keys(
        self, host: str, leader_key_path: str, follower: str, follower_user: str
    ):
        task = OrcehstratorTask(host, "setupServerSSHKeys")
        task.set_params(
            {
                "leader_key_path": leader_key_path,
                "follower": follower,
                "follower_user": follower_user,
            }
        )
        self.add_task(task)
