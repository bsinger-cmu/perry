from .orchestrator import Orchestrator, OrchestrationTask
import random
import string
    
# Goal Orchestrator
class GoalOrchestrator(Orchestrator):
    def __init__(self, ansible_runner) -> None:
        super().__init__(ansible_runner, "goals/")

    # Generate random flag
    def generate_flag(self):
        flag = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
        return flag

    # Add given flag to host. returns flag contents
    def add_flag(self, host: str, flag_path: str, flag_contents: str, user: str, user_group: str):
        task = OrchestrationTask(host, "addFlag")
        task.set_params({'owner_user': user, 
                         'owner_group': user_group,
                         'flag_path': flag_path, 
                         'flag_contents': flag_contents
                         })
        
        self.add_task(task)
        return flag_contents

    # Create and add flag to host. returns flag contents
    def setup_flag(self, host: str, flag_path: str, user: str, user_group: str):
        flag = self.generate_flag()
        self.add_flag(host, flag_path, flag, user, user_group)
        return flag

    def setup_root_flag(self, host: str):
        flag = self.generate_flag()
        self.add_flag(host, '/root/flag.txt', flag, 'root', 'root')
        return flag
