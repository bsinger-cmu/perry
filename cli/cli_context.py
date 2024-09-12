from openstack.connection import Connection

from ansible.AnsibleRunner import AnsibleRunner
from attacker.Attacker import Attacker
from deployment_instance.DeploymentInstance import DeploymentInstance
from config.Config import Config
from emulator.emulator import Emulator


class PerryContext:
    def __init__(
        self,
        openstack_conn: Connection,
        ansible_runner: AnsibleRunner,
        config: Config,
        experiment_dir: str,
        experiment_id: str,
    ):
        self.openstack_conn = openstack_conn
        self.ansible_runner = ansible_runner
        self.config = config
        self.experiment_dir = experiment_dir
        self.experiment_id = None

        # Set by cli modules
        self.emulator: Emulator | None = None
        self.environment: DeploymentInstance | None = None
        self.attacker: Attacker | None = None
        self.defender = None
