from .orchestrator import Orchestrator, OrcehstratorTask


# Common Orchestrator
class CommonOrchestrator(Orchestrator):
    def __init__(self, ansible_runner) -> None:
        super().__init__(ansible_runner, "common/")

    def add_SSH_key(self, host: str, user: str, key_path: str):
        task = OrcehstratorTask(host, "addSSHKey")
        task.set_params({"user": user, "ssh_key_path": key_path})
        self.add_task(task)

    def allow_traffic(self, host: str, user: str, protocol: str, port_no: int):
        task = OrcehstratorTask(host, "allowTraffic")
        task.set_params({"user": user, "proto": protocol, "port_no": str(port_no)})
        self.add_task(task)

    def change_password(self, host: str, username: str, password: str):
        task = OrcehstratorTask(host, "changePassword")
        task.set_params({"user": username, "password": password})
        self.add_task(task)

    def check_file(self, host: str, file: str):
        task = OrcehstratorTask(host, "checkFile")
        task.set_params({"file_path": file})
        self.add_task(task)

    def create_directory(self, host: str, cpath: str, dmode: str):
        task = OrcehstratorTask(host, "createDirectory")
        task.set_params({"cpath": cpath, "dmode": dmode})
        self.add_task(task)

    def create_user(self, host: str, username: str, password: str):
        task = OrcehstratorTask(host, "createUser")
        task.set_params({"user": username, "password": password})
        self.add_task(task)

    def create_cron_job(self, host: str, job_cmd: str):
        task = OrcehstratorTask(host, "cronJob")
        task.set_params({"job_cmd": job_cmd})
        self.add_task(task)

    def copy_file(self, host: str, src: str, dst: str):
        task = OrcehstratorTask(host, "fileRemoteCopy")
        task.set_params({"source": src, "destination": dst})
        self.add_task(task)

    def git_clone(self, host: str, repo: str, dest: str):
        task = OrcehstratorTask(host, "gitClone")
        task.set_params({"git_repo": repo, "git_dest": dest})
        self.add_task(task)

    def install_package(self, host: str, package_name: str):
        task = OrcehstratorTask(host, "installPackage")
        task.set_params({"package": package_name})
        self.add_task(task)

    def reboot(self, host: str, timeout: int = 0):
        task = OrcehstratorTask(host, "reboot")
        task.set_params({"timeout": str(timeout)})
        self.add_task(task)

    def run_command(self, host: str, command: str):
        task = OrcehstratorTask(host, "runCommand")
        task.set_params({"command": command})
        self.add_task(task)

    def perform_service_action(self, host: str, service_name: str, state_name: str):
        task = OrcehstratorTask(host, "serviceAction")
        task.set_params({"service_name": service_name, "state_name": state_name})
        self.add_task(task)

    def test_playbook(self, host: str = "manageHost"):
        self.add_task(OrcehstratorTask(host, "testPlaybook"))
