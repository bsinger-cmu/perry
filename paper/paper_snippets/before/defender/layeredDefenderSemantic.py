# fmt: off
EQUIFAX_SUBNETS = {
    "webserver": "192.168.200.0/24",
    "database": "192.168.201.0/24",
}
WEBSERVER_PREFIX = "webserver"
DATABASE_PREFIX = "database"
NUM_DECOYS = 10
NUM_HONEYCREDS = 50
DECOY_IMAGE_NAME = "decoy"
DECOY_FLAVOR = "decoy_flavor"
DECOY_KEYPAIR = "decoy_keypair"
DECOY_SEC_GROUP = "decoy_sec_group"
ANSIBEL_SEC_GROUP = "ansible_sec_group"
ansible_runner = AnsibleRunner()
openstack_conn = openstack.connect(cloud="default")
elasticsearch_conn = Elasticsearch(
    ELASTIC_SERVER_IP,
    basic_auth=("elastic", ELASTIC_API_KEY),
)
def addr_in_subnet(subnet, addr):
    return ipaddress.ip_address(addr) in ipaddress.ip_network(subnet)
webserver_hosts = []
webserver_subnet = EQUIFAX_SUBNETS["webserver"]
for server in conn.compute.servers():  # type: ignore
    if not server.name.startswith(WEBSERVER_PREFIX):
        continue
    for network, network_attrs in server.addresses.items():
        ip_addresses = [x["addr"] for x in network_attrs]
        for ip in ip_addresses:
            if addr_in_subnet(webserver_subnet, ip):
                webserver_hosts.append(ip)
database_hosts = []
database_subnet = EQUIFAX_SUBNETS["database"]
for server in conn.compute.servers():  # type: ignore
    if not server.name.startswith(DATABASE_PREFIX):
        continue
    for network, network_attrs in server.addresses.items():
        ip_addresses = [x["addr"] for x in network_attrs]
        for ip in ip_addresses:
            if addr_in_subnet(database_subnet, ip):
                database_hosts.append(ip)
decoy_ips = []
for _ in range(0, NUM_DECOYS):
    subnet = random.choice(EQUIFAX_SUBNETS)
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
    openstack_conn.compute.wait_for_server(server, wait=240)
    openstack_conn.compute.add_security_group_to_server(server, security_group)
    openstack_conn.compute.add_security_group_to_server(server, ansible_security_group)
    server_ip = None
    for network in server.addresses:
        if network == action.network:
            server_ip = server.addresses[network][0]["addr"]
            break
    if server_ip is None:
        raise Exception("Could not find ip for server")
    ansible_runner.run_playbook(check_if_host_up_pb, server_ip)
    ansible_runner.run_playbook(reset_ssh_config_pb, server_ip, "tomcat")
    ansible_runner.run_playbook(
        setup_decoy_service_pb, server_ip, ELASTIC_SEVER_IP, ELASTIC_API_KEY
    )
decoy_users = []
for _ in range(0, NUM_HONEYCREDS):
    subnet = random.choice(EQUIFAX_SUBNETS)
    host_ip = random.choice(webserver_hosts + database_hosts)
    decoy_ip = random.choice(decoy_ips)
    name = fake.name()
    decoy_username = name.replace(" ", "")
    decoy_password = fake.password()
    ansible_runner.run_playbook(
        create_user_ansible_pb, host_ip, decoy_username, decoy_password
    )
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
    decoy_users.append(deploy_honeycred(host_ip, decoy_ip))
parsed_telemetry_ids = []
while True:
    last_ten_second_query = {
        "bool": {
            "must": [
                {"range": {"@timestamp": {"gte": "now-10s"}}},
            ]
        }
    }
    sysflow_data = elasticsearch_conn.search(
        index="sysflow", query=last_ten_second_query
    )
    raw_telemetry = alert_query_data["hits"]["hits"]
    raw_telemetry += sysflow_data["hits"]["hits"]
    new_telemetry = [
        alert for alert in raw_telemetry if alert["_id"] not in parsed_telemetry_ids
    ]
    new_document_ids = [alert["_id"] for alert in new_telemetry]
    parsed_telemetry_ids.update(new_document_ids)
    for alert in new_telemetry:
        alert_data = alert["_source"]
        if alert_data["event"]["category"] == "process":
            if alert_data["process"]["name"] == "ssh":
                for decoy_user in decoy_users:
                    if decoy_user in alert_data["process"]["command_line"]:
                        server_ip = alert_data["process"]["ip"]
                        server = None
                        for server in conn.compute.servers():
                            for _, network_attrs in server.addresses.items():
                                ip_addresses = [x["addr"] for x in network_attrs]
                                if server_ip in ip_addresses:
                                    server = server
                        if server:
                            server_password = (
                                openstack_conn.compute.get_server_password(server.id)
                            )
                            openstack_conn.compute.rebuild_server(
                                server,
                                image=server.image.id,
                                name=server.name,
                                admin_password=server_password,
                            )
        if alert_data["event"]["category"] == "network":
            if "destination" in alert_data:
                if (
                    alert_data["destination"]["port"] == 22
                    and alert_data["destination"]["ip"] in decoy_ips
                ):
                    source_server_ip = alert_data["source"]["ip"]
                    target_server_ip = alert_data["destination"]["ip"]
                    source_server = None
                    target_server = None
                    for server in conn.compute.servers():
                        for _, network_attrs in server.addresses.items():
                            ip_addresses = [x["addr"] for x in network_attrs]
                            if source_server_ip in ip_addresses:
                                source_server = server
                            if target_server_ip in ip_addresses:
                                target_server = server
                    if source_server:
                        server_password = openstack_conn.compute.get_server_password(
                            source_server_ip.id
                        )
                        openstack_conn.compute.rebuild_server(
                            source_server_ip,
                            image=source_server_ip.image.id,
                            name=source_server_ip.name,
                            admin_password=server_password,
                        )
                    if target_server:
                        server_password = openstack_conn.compute.get_server_password(
                            target_server.id
                        )
                        openstack_conn.compute.rebuild_server(
                            target_server,
                            image=target_server.image.id,
                            name=target_server.name,
                            admin_password=server_password,
                        )
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
