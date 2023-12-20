from .orchestrator import Orchestrator, OrcehstratorTask
import random
import string


# Goal Orchestrator
class GoalOrchestrator(Orchestrator):
    def __init__(self, ansible_runner) -> None:
        super().__init__(ansible_runner, "goals/")

    # Generate random flag
    def generate_flag(self):
        flag = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(32)
        )
        return flag

    # Add given flag to host. returns flag contents
    def add_flag(
        self, host: str, flag_path: str, flag_contents: str, user: str, user_group: str
    ):
        task = OrcehstratorTask(host, "addFlag")
        task.set_params(
            {
                "owner_user": user,
                "owner_group": user_group,
                "flag_path": flag_path,
                "flag_contents": flag_contents,
            }
        )

        self.add_task(task)
        return flag_contents

    # Create and add flag to host. returns flag contents
    def setup_flag(
        self, host: str, flag_path: str, flag_contents: str, user: str, user_group: str
    ):
        self.add_flag(host, flag_path, flag_contents, user, user_group)

    def setup_root_flag(self, host: str, flag_contents: str):
        self.add_flag(host, "/root/flag.txt", flag_contents, "root", "root")
