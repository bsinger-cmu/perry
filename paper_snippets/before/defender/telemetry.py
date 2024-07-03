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
