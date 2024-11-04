from .OpenstackActuator import OpenstackActuator
from openstack_helper_functions.server_helpers import find_server_by_ip

sensitive_subnets = ["192.168.202", "192.168.198"]

from utility.logging import log_event


class RestoreServer(OpenstackActuator):

    def actuate(self, action):
        # Defender can't restore attacker server
        # TODO use environment service to check this
        for subnet in sensitive_subnets:
            if subnet in action.host_ip:
                log_event("Restore Service", f"Skipping: {action.host_ip}")
                return

        server = find_server_by_ip(self.openstack_conn, action.host_ip)

        if server and not server.status == "ACTIVE":
            log_event("Actuator restoring server: ", f"Skipping: {action.host_ip}")
            server_password = self.openstack_conn.compute.get_server_password(server.id)
            self.openstack_conn.compute.rebuild_server(
                server,
                image=server.image.id,
                name=server.name,
                admin_password=server_password,
            )
