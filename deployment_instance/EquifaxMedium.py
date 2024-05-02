from .EquifaxInstance import EquifaxInstance
from ansible.AnsibleRunner import AnsibleRunner


class EquifaxMedium(EquifaxInstance):
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        caldera_ip,
    ):
        topology = "equifax_medium"
        super().__init__(ansible_runner, openstack_conn, caldera_ip, topology)
