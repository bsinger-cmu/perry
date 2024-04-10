import json
import os
import time
from deployment_instance.topology_orchestrator import deploy_network, destroy_network
from deployment_instance.MasterOrchestrator import MasterOrchestrator
from colorama import Fore, Style
from rich import print as rprint
from openstack.connection import Connection
from ansible.AnsibleRunner import AnsibleRunner
from openstack import exceptions as openstackExceptions


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
    def __init__(self, ansible_runner: AnsibleRunner, openstack_conn, external_ip):
        self.ansible_runner: AnsibleRunner = ansible_runner
        self.openstack_conn: Connection = openstack_conn
        self.ssh_key_path = "./environment/ssh_keys/"
        self.caldera_ip = external_ip
        self.orchestrator = MasterOrchestrator(self.ansible_runner)
        self.all_instances = None
        self.topology = None

        self.hosts = {}

        self.flags = {}
        self.root_flags = {}

        self.find_management_server(external_ip)

    # Protofunction, this is where you define everything needed to setup the instance
    def compile_setup(self):
        return

    def runtime_setup(self):
        return

    def compile(self, setup_network=True, setup_hosts=True):
        if setup_network:
            # Redeploy entire network
            self.deploy_topology()
            time.sleep(5)

        if setup_hosts:
            # Setup instances
            self.compile_setup()
            # Save instance
            self.save_all_snapshots()

    def run(self):
        # Load snapshots
        self.load_all_snapshots()
        time.sleep(10)
        # Do runtime setup
        self.runtime_setup()

    def deploy_topology(self):
        destroy_network(self.topology)
        deploy_network(self.topology)

    def find_management_server(self, external_ip):
        manage_server, manage_ip = find_manage_server(self.openstack_conn, external_ip)
        rprint(f"Found management server: {manage_ip}")
        self.ansible_runner.update_management_ip(manage_ip)

    def check_flag(self, flag):
        if flag in self.flags:
            return self.flags[flag]
        return 0

    def save_flags(self, file_name="flags.json"):
        with open(os.path.join("temp_flags", file_name), "w") as f:
            json.dump(self.flags, f)

    def save_root_flags(self, file_name="root_flags.json"):
        with open(os.path.join("temp_flags", file_name), "w") as f:
            json.dump(self.root_flags, f)

    def save_all_flags(self, file_name="flags.json", root_file_name="root_flags.json"):
        rprint("Saving all flags to file...")
        self.save_flags(file_name)
        self.save_root_flags(root_file_name)

    def load_flags(self, file_name="flags.json"):
        with open(os.path.join("temp_flags", file_name), "r") as f:
            self.flags = json.load(f)

    def load_root_flags(self, file_name="root_flags.json"):
        with open(os.path.join("temp_flags", file_name), "r") as f:
            self.root_flags = json.load(f)

    def load_all_flags(self, file_name="flags.json", root_file_name="root_flags.json"):
        rprint("Loading all flags from file...")
        self.load_flags(file_name)
        self.load_root_flags(root_file_name)

    def print_all_flags(self):
        rprint("Flags:")
        for host, flag in self.flags.items():
            rprint(f"\t{host}: '{flag}'")
        rprint("Root Flags:")
        for host, flag in self.root_flags.items():
            rprint(f"\t{host}: '{flag}'")

    def _load_instances(self):
        if self.all_instances is None:
            self.all_instances = self.openstack_conn.list_servers()

    def save_snapshot(self, host_addr, snapshot_name, overwrite=True, wait=False):
        try:
            image = self.openstack_conn.get_image(snapshot_name)
            if image and overwrite:
                rprint(f"Image '{snapshot_name}' already exists. Deleting...")
                self.openstack_conn.delete_image(image.id, wait=True)
            elif image and not overwrite:
                rprint(f"Image '{snapshot_name}' already exists. Aborting...")
                return
            else:
                rprint(f"Image '{snapshot_name}' does not exist. Creating...")
        except:
            print("Multiple images with the same name exist. Aborting...")
            return

        self._load_instances()
        instance_iter = filter(lambda x: x.private_v4 == host_addr, self.all_instances)
        instance = list(instance_iter)[0]

        if instance:
            print(f"Creating snapshot {snapshot_name} for instance {instance.id}...")
            image = self.openstack_conn.create_image_snapshot(
                snapshot_name, instance.id, wait=wait
            )
            if image:
                print(
                    f"Successfully created snapshot {snapshot_name} with id {image.id}"
                )
            return image.id

    def load_snapshot(self, host_addr, snapshot_name, wait=False):
        self._load_instances()
        instance_iter = filter(lambda x: x.private_v4 == host_addr, self.all_instances)
        instance = list(instance_iter)[0]

        if instance:
            image = self.openstack_conn.get_image(snapshot_name)
            if image:
                print(
                    f"Loading snapshot {snapshot_name} for instance {instance.name}..."
                )
                self.openstack_conn.rebuild_server(
                    instance.id, image.id, wait=wait, admin_pass=None
                )
                if wait:
                    print(
                        f"Successfully loaded snapshot {snapshot_name} with id {image.id}"
                    )
            return instance.id

    def save_all_snapshots(self, wait=True):
        rprint("Saving all snapshots...")
        self._load_instances()
        images = []
        for instance in self.all_instances:
            image = self.save_snapshot(
                instance.private_v4, instance.name + "_image", overwrite=True
            )
            images.append(image)

        if wait:
            rprint("Waiting for all images to be saved...")
            all_active = False
            while not all_active:
                all_active = True
                rprint(f"\n{'Status':<12}{'Name'}")
                for image in images:
                    curr_img = None
                    try:
                        curr_img = self.openstack_conn.get_image_by_id(image)
                    except openstackExceptions.ResourceNotFound:
                        pass

                    if curr_img:
                        all_active = all_active and curr_img.status == "active"
                        color = Fore.GREEN if curr_img.status == "active" else Fore.RED
                        color = Fore.YELLOW if curr_img.status == "saving" else color
                        print(
                            f"{color}{curr_img.status:<12}{Style.RESET_ALL}{curr_img.name}"
                        )

                time.sleep(25)

    def load_all_snapshots(self, wait=True):
        rprint("Loading all snapshots...")
        self._load_instances()

        hosts = self.openstack_conn.list_servers()
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
