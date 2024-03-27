from ansible.AnsiblePlaybook import AnsiblePlaybook


class InstallSysFlow(AnsiblePlaybook):
    def __init__(self, hosts: str | list[str]) -> None:
        self.name = "defender/sysflow/install_sysflow.yml"
        self.params = {"host": hosts}
