import json
import os
import time
from deployment_instance.topology_orchestrator import deploy_network, destroy_network
from deployment_instance.MasterOrchestrator import MasterOrchestrator
from openstack_helper_functions import teardown_helper
from colorama import Fore, Style
from rich import print as rprint
import openstack
from openstack.connection import Connection
from openstack.exceptions import SDKException
from ansible.AnsibleRunner import AnsibleRunner
import config.Config as Config
from .openstack.openstack_processor import get_hosts_on_subnet

from utility.logging import get_logger

logger = get_logger()

NUM_PERMANENT_SUBNETS = 1
NUM_PERMANENT_NETS = 2
NUM_PERMANENT_SECURITY_GROUPS = 1


def find_manage_server(conn, external_ip):
    """Finds management server that can be used to talk to other servers
    Assumes only one server has floating ip and it is the management server"""

    # Remove last octet from external ip
    external_ip = ".".join(external_ip.split(".")[:3])

    for server in conn.compute.servers():
        for network, network_attrs in server.addresses.items():
            ip_addresses = [x["addr"] for x in network_attrs]
            for ip in ip_addresses:
                # Remove last octet from ip
                ip_subnet = ".".join(ip.split(".")[:3])
                if external_ip == ip_subnet:
                    return server, ip
    return None, None


class DeploymentInstance:
    def __init__(
        self,
        ansible_runner: AnsibleRunner,
        openstack_conn,
        external_ip,
        config: Config.Config,
    ):
        self.ansible_runner: AnsibleRunner = ansible_runner
        self.openstack_conn: Connection = openstack_conn
        self.ssh_key_path = "./environment/ssh_keys/"
        self.caldera_ip = external_ip
        self.config = config
        self.orchestrator = MasterOrchestrator(self.ansible_runner)
        self.all_instances = None
        self.topology = None

        self.hosts = {}

        self.flags = {}
        self.root_flags = {}

    # Protofunction, this is where you define everything needed to setup the instance
    def compile_setup(self):
        return

    def runtime_setup(self):
        return

    def parse_network(self):
        return

    def teardown(self):
        print("Tearing down...")

        conn = self.openstack_conn

        teardown_helper.delete_instances(conn)
        while conn.list_servers():
            time.sleep(0.5)

        teardown_helper.delete_floating_ips(conn)
        while conn.list_floating_ips():
            time.sleep(0.5)

        teardown_helper.delete_routers(conn)
        while conn.list_routers():
            time.sleep(0.5)

        teardown_helper.delete_subnets(conn)
        while len(conn.list_subnets()) > NUM_PERMANENT_SUBNETS:
            time.sleep(0.5)

        teardown_helper.delete_networks(conn)
        while len(conn.list_networks()) > NUM_PERMANENT_NETS:
            time.sleep(0.5)

        teardown_helper.delete_security_groups(conn)
        while len(conn.list_security_groups()) > NUM_PERMANENT_SECURITY_GROUPS:
            time.sleep(0.5)

    def compile(self, setup_network=True, setup_hosts=True):
        if setup_network:
            # Redeploy entire network
            self.deploy_topology()
            time.sleep(5)

        self.find_management_server()
        self.parse_network()

        if setup_hosts:
            # Setup instances
            self.compile_setup()

        # Save instance
        self.save_all_snapshots()

    def setup(self):
        self.find_management_server()
        self.parse_network()
        # Load snapshots
        self.load_all_snapshots()
        time.sleep(10)
        self.rebuild_error_hosts()

    def deploy_topology(self):
        self.teardown()
        deploy_network(self.topology)

    def find_management_server(self):
        manage_server, manage_ip = find_manage_server(
            self.openstack_conn, self.caldera_ip
        )
        logger.debug(f"Found management server: {manage_ip}")
        self.ansible_runner.update_management_ip(manage_ip)

    def _load_instances(self):
        self.all_instances = self.openstack_conn.list_servers()

    def save_snapshot(self, instance, snapshot_name):
        image = self.openstack_conn.get_image(snapshot_name)
        if image:
            logger.debug(f"Image '{snapshot_name}' already exists. Deleting...")
            self.openstack_conn.delete_image(image.id, wait=True)  # type: ignore

        logger.debug(f"Creating snapshot {snapshot_name} for instance {instance.id}...")
        image = self.openstack_conn.create_image_snapshot(
            snapshot_name, instance.id, wait=True
        )
        return image.id

    def load_snapshot(self, host_addr, snapshot_name, wait=False):
        self._load_instances()
        instance_iter = filter(lambda x: x.private_v4 == host_addr, self.all_instances)
        instance = list(instance_iter)[0]

        if instance:
            image = self.openstack_conn.get_image(snapshot_name)
            if image:
                logger.debug(
                    f"Loading snapshot {snapshot_name} for instance {instance.name}..."
                )
                self.openstack_conn.rebuild_server(
                    instance.id, image.id, wait=wait, admin_pass=None
                )
                if wait:
                    logger.debug(
                        f"Successfully loaded snapshot {snapshot_name} with id {image.id}"
                    )
            return instance.id

    def save_all_snapshots(self, wait=True):
        logger.debug("Saving all snapshots...")
        self._load_instances()
        images = []
        for instance in self.all_instances:
            image = self.save_snapshot(instance, instance.name + "_image")
            images.append(image)

    def load_all_snapshots(self, wait=True):
        logger.debug("Loading all snapshots...")
        self._load_instances()
        hosts = self.openstack_conn.list_servers()

        # Check if all images exist
        for host in hosts:
            image = self.openstack_conn.get_image(host.name + "_image")
            if not image:
                raise Exception(f"Image {host.name + '_image'} does not exist")

        rebuild_num = 10
        # Rebuild 10 servers at a time
        for i in range(0, len(hosts), rebuild_num):
            hosts_to_restore = []
            if i + 5 < len(hosts):
                hosts_to_restore = hosts[i : i + rebuild_num]
            else:
                hosts_to_restore = hosts[i:]

            # Start rebuilding all servers
            for host in hosts_to_restore:
                self.load_snapshot(host.private_v4, host.name + "_image", wait=False)

            # Wait for rebuild to start
            time.sleep(5)

            # Wait for 5 servers to be rebuilt
            waiting_for_rebuild = True
            while waiting_for_rebuild:
                waiting_for_rebuild = False
                for host in hosts_to_restore:
                    curr_host = self.openstack_conn.get_server_by_id(host.id)
                    if curr_host and curr_host.status == "REBUILD":
                        waiting_for_rebuild = True

                time.sleep(1)
        return

    def get_error_hosts(self):
        hosts = self.openstack_conn.list_servers()
        error_hosts = []

        for host in hosts:
            if host.status == "ERROR":
                error_hosts.append(host)

        return error_hosts

    def rebuild_error_hosts(self):
        error_hosts = self.get_error_hosts()
        for host in error_hosts:
            self.openstack_conn.delete_server(host.id, wait=True)
            self.load_snapshot(host.private_v4, host.name + "_image", wait=True)

        error_hosts = self.get_error_hosts()
        if len(error_hosts) > 0:
            raise Exception("Error hosts still exist after rebuild")
        return
