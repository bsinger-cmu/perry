# Ignore type hinting
# type: ignore

EQUIFAX_SUBNETS = {
    "webserver": "192.168.200.0/24",
    "database": "192.168.201.0/24",
}
NUM_DECOYS = 10
NUM_HONEYCREDS = 50

# Manual class implemented by user to run ansible playbooks
ansible_runner = AnsibleRunner()

# Openstack connection to SDK
openstack_conn = openstack.connect(cloud="default")

# Elasticsearch connection
elasticsearch_conn = Elasticsearch(
    ELASTIC_SERVER_IP,
    basic_auth=("elastic", ELASTIC_API_KEY),
)


# Deploy decoys
decoy_ips = []
for _ in range(0, NUM_DECOYS):
    subnet = random.choice(EQUIFAX_SUBNETS)
    # Low-level calls to Openstack SDK
    image = openstack_conn.get_image(DECOY_IMAGE_NAME)
    flavor = openstack_conn.compute.find_flavor(DECOY_FLAVOR)
    # ...
    server = openstack_conn.compute.create_server(
        name=action.server,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}],
        key_name=keypair.name,
    )
    openstack_conn.compute.add_security_group_to_server(...)
    # ...
    # Low-level calls to manually created Ansible playbooks
    ansible_runner.run_playbook(check_if_host_up_pb, server_ip)
    ansible_runner.run_playbook(reset_ssh_config_pb, server_ip, "tomcat")
    # ...
# Deploy honeycreds
decoy_users = []
for _ in range(0, NUM_HONEYCREDS):
    subnet = random.choice(EQUIFAX_SUBNETS)
    # Use Openstack SDK to get hosts in subnet
    # ...
    # Deploy decoy credential on a random host
    host_ip = random.choice(ips_in_subnet)
    decoy_ip = random.choice(decoy_ips)
    # Generate fake user and password
    name = fake.name()
    decoy_username = name.replace(" ", "")
    decoy_password = fake.password()
    # Create fake user on dst host
    ansible_runner.run_playbook(
        create_user_ansible_pb, action.honey_host.ip, decoy_username, decoy_password
    )
    # Get users on src host
    users = ansible_runner.run_playbook(get_users_ansible_pb, src_host_ip)
    # Setup ssh keys on each user using Ansible
    # ...


DECOY_IMAGE_NAME = "decoy"
DECOY_FLAVOR = "decoy_flavor"
DECOY_KEYPAIR = "decoy_keypair"
DECOY_SEC_GROUP = "decoy_sec_group"
ANSIBEL_SEC_GROUP = "ansible_sec_group"


def deploy_decoy(subnet):
    # Check if decoy image already exists
    image = openstack_conn.get_image(DECOY_IMAGE_NAME)

    flavor = openstack_conn.compute.find_flavor(DECOY_FLAVOR)
    network = openstack_conn.network.find_network(subnet)
    keypair = openstack_conn.compute.find_keypair(DECOY_KEYPAIR)
    security_group = openstack_conn.network.find_security_group(DECOY_SEC_GROUP)
    ansible_security_group = openstack_conn.network.find_security_group(
        ANSIBEL_SEC_GROUP
    )

    server = openstack_conn.compute.create_server(
        name=action.server,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}],
        key_name=keypair.name,
    )

    # Wait for server to be created
    openstack_conn.compute.wait_for_server(server, wait=240)

    # Add security groups
    openstack_conn.compute.add_security_group_to_server(server, security_group)
    openstack_conn.compute.add_security_group_to_server(server, ansible_security_group)

    server_ip = None
    # get interal network ip
    for network in server.addresses:
        if network == action.network:
            server_ip = server.addresses[network][0]["addr"]
            break

    if server_ip is None:
        raise Exception("Could not find ip for server")

    # Wait for host to start
    ansible_runner.run_playbook(check_if_host_up_pb, server_ip)
    # Reset ssh config
    ansible_runner.run_playbook(reset_ssh_config_pb, server_ip, "tomcat")
    # Deploy decoy service
    ansible_runner.run_playbook(
        setup_decoy_service_pb, server_ip, ELASTIC_SEVER_IP, ELASTIC_API_KEY
    )


def deploy_decoy_credential(src_host_ip, dst_host_ip):
    name = fake.name()
    decoy_username = name.replace(" ", "")
    decoy_password = fake.password()

    # Create fake user on dst host
    ansible_runner.run_playbook(
        create_user_ansible_pb, action.honey_host.ip, decoy_username, decoy_password
    )
    # Get users on src host
    users = ansible_runner.run_playbook(get_users_ansible_pb, src_host_ip)

    for user in users:
        ansible_runner.run_playbook(
            setup_ssh_keys_ansible_pb,
            src_host_ip,
            user,
            dst_host_ip,
            decoy_username,
        )
        ansible_runner.run_playbook(add_fake_data_pb, src_host_ip, user, "~/decoy.json")


#### In seperate YML files, manually created by the developer ####
create_user_ansible_pb = [
    {
        "hosts": "{{ host }}",
        "remote_user": "root",
        "tasks": [
            {
                "name": "Add user",
                "ansible.builtin.user": {
                    "name": "{{ user }}",
                    "password": "{{ password | password_hash('sha512') }}",
                    "shell": "/bin/bash",
                    "group": "admin",
                },
            }
        ],
    }
]

setup_ssh_keys_ansible_pb = [
    {
        "hosts": "{{ host }}",
        "tasks": [
            {
                "name": "create .ssh directory",
                "become": true,
                "become_user": "{{ host_user }}",
                "file": {"path": "~/.ssh", "state": "directory", "mode": "0700"},
            },
            {
                "name": "copy key bair",
                "become": true,
                "become_user": "{{ host_user }}",
                "copy": {
                    "src": "ssh_keys/id_rsa",
                    "dest": "~/.ssh/id_rsa",
                    "mode": "0600",
                },
            },
            {
                "name": "add to ssh config",
                "become": true,
                "become_user": "{{ host_user }}",
                "blockinfile": {
                    "state": "present",
                    "insertafter": "EOF",
                    "dest": "~/.ssh/config",
                    "content": "Host {{ follower_user }}\n  HostName {{ follower }}\n  User {{ follower_user }}\n  IdentityFile ~/.ssh/id_rsa\n",
                    "create": true,
                    "mode": "0600",
                    "marker": "",
                },
            },
        ],
    },
    {
        "hosts": "{{ follower }}",
        "tasks": [
            {
                "name": "add leader public key to followers",
                "authorized_key": {
                    "user": "{{ follower_user }}",
                    "key": "{{ lookup('file', 'ssh_keys/id_rsa.pub') }}",
                },
            }
        ],
    },
]

add_to_ssh_config_ansible_pb = [
    {
        "hosts": "{{ host }}",
        "tasks": [
            {
                "name": "create .ssh directory",
                "become": true,
                "become_user": "{{ host_user }}",
                "file": {"path": "~/.ssh", "state": "directory", "mode": "0700"},
            },
            {
                "name": "add to ssh config",
                "become": true,
                "become_user": "{{ host_user }}",
                "blockinfile": {
                    "state": "present",
                    "insertafter": "EOF",
                    "dest": "~/.ssh/config",
                    "content": "Host {{ follower_user }}\n  HostName {{ follower }}\n  User {{ follower_user }}\n  IdentityFile ~/.ssh/id_rsa\n",
                    "create": true,
                    "mode": "0600",
                    "marker": "",
                },
            },
        ],
    }
]

add_fake_data_pb = [
    {
        "hosts": "{{ host }}",
        "become": true,
        "become_user": "{{ host_user }}",
        "tasks": [
            {
                "name": "Copy ssh config",
                "ansible.builtin.copy": {"src": "data.json", "dest": "{{ path }}"},
            }
        ],
    }
]

check_if_host_up_pb = [
    {
        "hosts": "{{ host }}",
        "gather_facts": "no",
        "remote_user": "root",
        "tasks": [
            {
                "name": "Wait for host to go up",
                "wait_for_connection": {"delay": 0, "timeout": 60},
            },
            {"name": "Gathering facts", "setup": null},
        ],
    }
]

reset_ssh_config_pb = [
    {
        "hosts": "{{ host }}",
        "tasks": [
            {
                "name": "delete ssh copnfig",
                "become": true,
                "become_user": "{{ host_user }}",
                "file": {"path": "~/.ssh/config", "state": "absent"},
            },
            {
                "name": "Touch ssh copnfig",
                "become": true,
                "become_user": "{{ host_user }}",
                "file": {"path": "~/.ssh/config", "state": "touch", "mode": "0600"},
            },
        ],
    }
]

setup_decoy_service_pb = [
    {
        "hosts": "{{ host }}",
        "remote_user": "root",
        "tasks": [
            {
                "name": "Install pip",
                "ansible.builtin.apt": {
                    "name": "python3-pip",
                    "state": "present",
                    "update_cache": "yes",
                },
            },
            {
                "name": "Install honeyservice package",
                "ansible.builtin.pip": {
                    "name": "git+https://github.com/DeceptionProjects/FakeNetworkServices.git"
                },
            },
            {
                "name": "Run honey service",
                "command": 'python3 -m fake_network_services.FakeNetworkService -p {{ port_no }} -s {{ service }} -l {{ elasticsearch_server }} --api-key="{{ elasticsearch_api_key }}"',
                "async": 1000,
                "poll": 0,
            },
        ],
    }
]
