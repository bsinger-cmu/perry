from ansible.AnsibleRunner import AnsibleRunner


class OpenstackActuator:
    def __init__(
        self,
        openstack_conn,
        ansible_runner: AnsibleRunner,
        external_elasticsearch_server,
        elasticsearch_api_key,
    ):
        self.openstack_conn = openstack_conn
        self.ansible_runner = ansible_runner

        # Telemetry information
        self.external_elasticsearch_server = external_elasticsearch_server
        self.elasticsearch_api_key = elasticsearch_api_key
        return

    # Subclass overwrites to run action
    def actuate(self, action):
        return
