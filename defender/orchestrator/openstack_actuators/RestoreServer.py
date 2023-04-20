from .OpenstackActuator import OpenstackActuator
from openstack_helper_functions.server_helpers import find_server_by_ip


class RestoreServer(OpenstackActuator):

    def actuate(self, action):
        server = find_server_by_ip(self.openstack_conn, action.host_ip)

        if server:
            server_password = self.openstack_conn.compute.get_server_password(server.id)
            self.openstack_conn.compute.rebuild_server(server, image=server.image.id, name=server.name, admin_password=server_password)