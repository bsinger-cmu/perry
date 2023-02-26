from .OpenstackActuator import OpenstackActuator
from openstack_helper_functions.server_helpers import shutdown_server_by_ip


class DeployDecoy(OpenstackActuator):

    SERVER_NAME = 'decoy'
    IMAGE_NAME = 'Ubuntu20'
    KEYPAIR_NAME = 'cage'
    FLAVOR_NAME = 'm1.small'
    NETWORK_NAME = 'internal_network'


    def actuate(self, action):
        # Create server
        image = self.openstack_conn.image.find_image(self.IMAGE_NAME)
        flavor = self.openstack_conn.compute.find_flavor(self.FLAVOR_NAME)
        network = self.openstack_conn.network.find_network(self.NETWORK_NAME)
        keypair = self.openstack_conn.compute.find_keypair(self.KEYPAIR_NAME)
        security_group = self.openstack_conn.network.find_security_group('simple')

        server = self.openstack_conn.compute.create_server(
            name=self.SERVER_NAME, image_id=image.id, flavor_id=flavor.id,
            networks=[{"uuid": network.id}], key_name=keypair.name
        )
        
        # Wait for server to be created
        server = self.openstack_conn.compute.wait_for_server(server)

        # Add security group
        self.openstack_conn.compute.add_security_group_to_server(server, security_group)

        # Deploy honey services
        server_ip = None
        # get interal network ip
        for network in server.addresses:
            if network == 'internal_network':
                server_ip = server.addresses[network][0]['addr']

        if server_ip is None:
            raise Exception('Could not find ip for server')
        
        params = {'host': server_ip}
        self.ansible_runner.run_playbook('defender/deploy_honey_ssh.yml', playbook_params=params)