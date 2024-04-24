import time
from .OpenstackActuator import OpenstackActuator
from ansible.defender import DeployHoneyService
from ansible.vulnerabilities import SetupStrutsVulnerability
from defender.capabilities import StartHoneyService

from openstack_helper_functions.server_helpers import shutdown_server_by_ip


class DeployDecoy(OpenstackActuator):
    def actuate(self, action):
        # Create server
        image = self.openstack_conn.image.find_image(action.image)
        flavor = self.openstack_conn.compute.find_flavor(action.flavor)
        network = self.openstack_conn.network.find_network(action.network)
        keypair = self.openstack_conn.compute.find_keypair(action.keypair)
        security_group = self.openstack_conn.network.find_security_group(
            action.sec_group
        )
        manage_security_group = self.openstack_conn.network.find_security_group(
            "talk_to_manage"
        )

        print("Creating decoy server...")
        server = self.openstack_conn.compute.create_server(
            name=action.server,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
            key_name=keypair.name,
        )

        # Wait for server to be created
        print("Waiting for decoy server to be created...")
        server = self.openstack_conn.compute.wait_for_server(server, wait=240)

        # Add security group
        print("Adding security groups...")
        self.openstack_conn.compute.add_security_group_to_server(server, security_group)
        self.openstack_conn.compute.add_security_group_to_server(
            server, manage_security_group
        )

        # Deploy honey services
        server_ip = None
        # get interal network ip
        print("Getting decoy server ip address...")
        for network in server.addresses:
            if network == action.network:
                server_ip = server.addresses[network][0]["addr"]
                break

        print(f"Decoy server ip address is {server_ip}")
        action.host.ip = server_ip

        if server_ip is None:
            raise Exception("Could not find ip for server")

        time.sleep(10)

        if action.apacheVulnerability:
            print("Deploying apache vulnerability...")
            self.ansible_runner.run_playbook(SetupStrutsVulnerability(server_ip))

        if action.honeySSHService:
            print("Deploying honey service...")
            honey_service_action = StartHoneyService(server_ip)
            honey_service_pb = DeployHoneyService(
                honey_service_action,
                self.external_elasticsearch_server,
                self.elasticsearch_api_key,
            )
            self.ansible_runner.run_playbook(honey_service_pb)
