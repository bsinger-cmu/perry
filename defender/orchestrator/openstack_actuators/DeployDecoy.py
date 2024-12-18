import time
from .OpenstackActuator import OpenstackActuator
from ansible.defender import DeployHoneyService
from ansible.vulnerabilities import SetupStrutsVulnerability
from defender.capabilities import StartHoneyService
from ansible.deployment_instance import CheckIfHostUp, ResetSSHConfig

from openstack_helper_functions.server_helpers import shutdown_server_by_ip


class DeployDecoy(OpenstackActuator):
    def actuate(self, action):
        # Check if decoy image already exists
        image = self.openstack_conn.get_image("decoy")
        image_exists = image is not None

        manage_image_used = False
        web_image_used = False

        if not image_exists:
            if action.apacheVulnerability:
                # Use a webserver image
                manage_image = self.openstack_conn.image.find_image("manage_A_0_image")
                web_image = self.openstack_conn.image.find_image("webserver_0_image")
                
                if manage_image is not None:
                    image = manage_image
                    manage_image_used = True
                elif web_image is not None:
                    image = web_image
                    web_image_used = True
                else:
                    raise Exception("Error decoy image not found")
            else:
                # Create server
                image = self.openstack_conn.image.find_image(action.image)

        flavor = self.openstack_conn.compute.find_flavor(action.flavor)
        network = self.openstack_conn.network.find_network(action.network)
        keypair = self.openstack_conn.compute.find_keypair(
            self.config.openstack_config.ssh_key_name
        )
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
        self.openstack_conn.compute.wait_for_server(server, wait=240)

        # Add security group
        print("Adding security groups...")
        self.openstack_conn.compute.add_security_group_to_server(server, security_group)
        self.openstack_conn.compute.add_security_group_to_server(
            server, manage_security_group
        )

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

        self.ansible_runner.run_playbook(CheckIfHostUp(server_ip))

        if not image_exists:
            if action.apacheVulnerability:
                print("Deploying apache vulnerability...")
                print("Reseting ssh config")
                
                name = 'tomcat'
                if manage_image_used:
                    name = 'manageA0'
                
                self.ansible_runner.run_playbook(ResetSSHConfig(server_ip, name))
                time.sleep(5)

            if action.honeySSHService:
                print("Deploying honey service...")
                honey_service_action = StartHoneyService(server_ip)
                honey_service_pb = DeployHoneyService(
                    honey_service_action,
                    self.external_elasticsearch_server,
                    self.elasticsearch_api_key,
                )
                self.ansible_runner.run_playbook(honey_service_pb)

            # Create image
            print("Creating decoy image...")
            image = self.openstack_conn.compute.create_server_image(
                server, "decoy", wait=True
            )
