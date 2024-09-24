import openstack
from openstack.exceptions import SDKException


# Deleting instances
def delete_instances(conn):
    servers = conn.list_servers()
    for server in servers:
        current_sgs = server.security_groups

        if current_sgs:
            # Remove each security group from the server
            for sg in current_sgs:
                # Debug the structure of each security group object
                sg_name = sg.get("id")
                if sg_name:
                    conn.remove_server_security_groups(server, sg_name)

        conn.delete_server(server.id)


# Deleting floating ips
def delete_floating_ips(conn):
    floating_ips = conn.list_floating_ips()
    for floating_ip in floating_ips:
        try:
            conn.delete_floating_ip(floating_ip.id)
        except SDKException:
            pass


# Delete routers
def delete_routers(conn):
    for router in conn.list_routers():

        # First, detach all router interfaces
        for port in conn.list_ports():
            if port.device_owner == "network:router_interface":
                subnet_id = port.fixed_ips[0]["subnet_id"]
                conn.remove_router_interface(router, subnet_id=subnet_id)

        # Finally, delete the router
        conn.delete_router(router.id)


# Delete all ports
def delete_ports(conn):
    # Attempt to delete all associated ports
    networks = conn.list_networks()
    for network in networks:
        # Get all ports associated with the network
        ports = conn.list_ports()
        for port in ports:
            try:
                conn.delete_port(port.id)
            except SDKException:
                pass


def delete_subnets(conn):
    subnets = conn.list_subnets()
    for subnet in subnets:
        try:
            conn.delete_subnet(subnet.id)
        except SDKException:
            pass


def delete_networks(conn):
    networks = conn.list_networks()
    for network in networks:
        try:
            conn.delete_network(network.id)
        except SDKException:
            pass


def delete_security_groups(conn):
    security_groups = conn.list_security_groups()
    for sg in security_groups:
        try:
            conn.delete_security_group(sg.id)
        except SDKException:
            pass


def check_resources_deleted(self):
    # Check Instances
    instances = list(self.openstack_conn.list_servers())

    # Check Floating IPs
    floating_ips = list(self.openstack_conn.list_floating_ips())

    # Check Routers
    routers = list(self.openstack_conn.list_routers())

    ports = list(self.openstack_conn.list_ports())

    # Check Networks
    networks = list(self.openstack_conn.list_networks())

    # Check Subnets
    subnets = list(self.openstack_conn.list_subnets())

    # Check Security Groups
    security_groups = list(self.openstack_conn.list_security_groups())

    return (
        not instances
        and not floating_ips
        and not routers
        and not ports
        and len(networks) == 2  # the external and shared network will be there
        and len(security_groups) == 1  # the default security group will be there
    )
