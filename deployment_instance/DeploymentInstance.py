import json
import os
import time
from deployment_instance.topology_orchestrator import deploy_network, destroy_network
from deployment_instance.MasterOrchestrator import MasterOrchestrator
from colorama import Fore, Style
from rich import print as rprint
from openstack.connection import Connection

public_ip = '10.20.20'
# Finds management server that can be used to talk to other servers
# Assumes only one server has floating ip and it is the management server
def find_manage_server(conn):
    for server in conn.compute.servers():
        for network, network_attrs in server.addresses.items():
            ip_addresses = [x['addr'] for x in network_attrs]
            for ip in ip_addresses:
                if public_ip in ip:
                    return server, ip
    return None, None
                
class DeploymentInstance:
    def __init__(self, ansible_runner, openstack_conn, caldera_ip):
        self.ansible_runner = ansible_runner
        self.openstack_conn: Connection = openstack_conn
        self.ssh_key_path = './environment/ssh_keys/'
        self.caldera_ip = caldera_ip
        self.orchestrator = MasterOrchestrator(self.ansible_runner)
        self.all_instances = None

        self.hosts = {}

        self.flags = {}
        self.root_flags = {}

        self.find_management_server()

    def find_management_server(self):
        manage_server, manage_ip = find_manage_server(self.openstack_conn)
        self.ansible_runner.update_management_ip(manage_ip)

    def check_flag(self, flag):
        if flag in self.flags:
            return self.flags[flag]
        return 0
    
    def save_flags(self, file_name="flags.json"):
        with open(os.path.join('temp_flags', file_name), 'w') as f:
            json.dump(self.flags, f)

    def save_root_flags(self, file_name="root_flags.json"):
        with open(os.path.join('temp_flags', file_name), 'w') as f:
            json.dump(self.root_flags, f)

    def save_all_flags(self, file_name="flags.json", root_file_name="root_flags.json"):
        rprint("Saving all flags to file...")
        self.save_flags(file_name)
        self.save_root_flags(root_file_name)

    def load_flags(self, file_name="flags.json"):
        with open(os.path.join('temp_flags', file_name), 'r') as f:
            self.flags = json.load(f)
    
    def load_root_flags(self, file_name="root_flags.json"):
        with open(os.path.join('temp_flags', file_name), 'r') as f:
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
            print(f'Creating snapshot {snapshot_name} for instance {instance.id}...')
            image = self.openstack_conn.create_image_snapshot(snapshot_name, instance.id, wait=wait)
            if image:
                print(f'Successfully created snapshot {snapshot_name} with id {image.id}')
            return image.id              

    def load_snapshot(self, host_addr, snapshot_name, wait=False):
        self._load_instances()
        instance_iter = filter(lambda x: x.private_v4 == host_addr, self.all_instances)
        instance = list(instance_iter)[0]
        
        if instance:
            image = self.openstack_conn.get_image(snapshot_name)
            if image:
                print(f'Loading snapshot {snapshot_name} for instance {instance.name}...')
                self.openstack_conn.rebuild_server(instance.id, image.id, wait=wait, admin_pass=None)
                if wait:
                    print(f'Successfully loaded snapshot {snapshot_name} with id {image.id}')
            return instance.id

    def save_all_snapshots(self, wait=True):
        rprint("Saving all snapshots...")
        self._load_instances()
        images = []
        for instance in self.all_instances:
            image = self.save_snapshot(instance.private_v4, instance.name + "_image", overwrite=True)
            images.append(image)

        if wait:
            rprint("Waiting for all images to be saved...")
            all_active = False
            while not all_active:
                all_active = True
                rprint(f"\n{'Status':<12}{'Name'}")
                for image in images:
                    curr_img = self.openstack_conn.get_image_by_id(image)
                    if curr_img:
                        all_active = all_active and curr_img.status == 'active'
                        color = Fore.GREEN if curr_img.status == 'active' else Fore.RED
                        color = Fore.YELLOW if curr_img.status == 'saving' else color
                        print(f"{color}{curr_img.status:<12}{Style.RESET_ALL}{curr_img.name}")
                time.sleep(25)
    
    def load_all_snapshots(self, wait=True):
        rprint("Loading all snapshots...")
        self._load_instances()
        
        # This is so that we do not try to load a snapshot while an instance is
        # being rebuilt. 
        waiting_for_rebuild = True
        while waiting_for_rebuild:
            waiting_for_rebuild = False
            for instance in self.all_instances:
                curr_instance = self.openstack_conn.get_server_by_id(instance.id)
                if curr_instance.status == 'REBUILD':
                    waiting_for_rebuild = True
                    rprint(f"Instance {Fore.RED}{curr_instance.name}{Style.RESET_ALL} is being rebuilt. Waiting...")
            if not waiting_for_rebuild:
                rprint("All instances are ready to be rebuilt.")
            else:
                time.sleep(10)

        waiting_for_active = True
        while waiting_for_active:
            waiting_for_active = False
            for instance in self.all_instances:
                curr_instance = self.openstack_conn.get_server_by_id(instance.id)
                if curr_instance.status == "SHUTOFF":
                    waiting_for_active = True
                    rprint(f"Starting instance {Fore.RED}{curr_instance.name}{Style.RESET_ALL}...")

                    task_state = curr_instance.task_state
                    if not task_state:
                        self.openstack_conn.compute.start_server(curr_instance.id)
                    else:
                        rprint(f"Instance {curr_instance.name} has task_state {task_state}. Skipping for now...")

        # Load all snapshots
        for instance in self.all_instances:
            self.load_snapshot(instance.private_v4, instance.name + "_image")
        
        # Wait for all instances to be active before doing anything else
        if wait:
            rprint("Waiting for all instances to be active...")
            all_active = False
            while not all_active:
                all_active = True
                rprint(f"\n{'Status':<12}{'Name'}")
                for instance in self.all_instances:
                    curr_instance = self.openstack_conn.get_server_by_id(instance.id)
                    if curr_instance:
                        all_active = all_active and curr_instance.status == 'ACTIVE'
                        color = Fore.GREEN if curr_instance.status == 'ACTIVE' else Fore.RED
                        color = Fore.YELLOW if curr_instance.status == 'REBUILD' else color

                        print(f"{color}{curr_instance.status:<12}{Style.RESET_ALL}{curr_instance.name}")
                        
                        if curr_instance.status == 'ERROR':
                            print("ERROR: Instance in error state. Aborting...")
                            return 1 ## Failure to load snapshots

                time.sleep(7)
        return 0
        # for instance in self.all_instances:
        #     curr_instance = self.openstack_conn.get_server_by_id(instance.id)
        #     print(f"[status {curr_instance.status}] - {curr_instance.name}")
        #     self.conn.wait_for_server(curr_instance, auto_ip=False)
                    


    def deploy_topology(self):
        destroy_network(self.topology)
        deploy_network(self.topology)

    def setup_instance(self, already_deployed=False):
        if not already_deployed:
            self.deploy_topology()
        self.setup()
    
    def setup(self):
        return
