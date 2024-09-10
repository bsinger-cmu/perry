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



# Telemetry conditions for decoy credential alert
# ...
# Restore if decoy credential used
server_ip = alert_data["process"]["ip"]
server = None
### Find server by ip in openstack
for server in conn.compute.servers():
    for _, network_attrs in server.addresses.items():
        # ...
### Use openstack to restore server
if server:
    server_password = openstack_conn.compute.get_server_password(server.id)
    openstack_conn.compute.rebuild_server(
        server,
        image=server.image.id,
        name=server.name,
        admin_password=server_password,
    )
# Telemetry conditions for decoy host alert...
## Restore host if decoy credential used
source_server_ip = alert_data["source"]["ip"]
target_server_ip = alert_data["destination"]["ip"]
source_server = None
target_server = None
### Find server by ip in openstack
for server in conn.compute.servers():
    for _, network_attrs in server.addresses.items():
        ip_addresses = [x["addr"] for x in network_attrs]
        # ...
### Use openstack to restore server
if source_server:
    server_password = (
        openstack_conn.compute.get_server_password(source_server_ip.id)
    )
    openstack_conn.compute.rebuild_server(...)
if target_server:
    server_password = (
        openstack_conn.compute.get_server_password(target_server.id)
    )
    openstack_conn.compute.rebuild_server(...)