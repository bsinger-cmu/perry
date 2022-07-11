import openstack
import ipaddress

def initialize():
    # Initialize connection
    conn = openstack.connect(cloud='default')
    return conn


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


def addr_in_subnet(subnet, addr):
    return ipaddress.ip_address(addr) in ipaddress.ip_network(subnet.cidr)


def server_is_on_subnet(subnet, server):
    for network, network_attrs in server.addresses.items():
        ip_addresses = [x['addr'] for x in network_attrs]
        for ip in ip_addresses:
            if addr_in_subnet(subnet, ip):
                return True


def servers_on_subnet(conn, subnet):
    hosts_in_subnet = []
    for server in conn.compute.servers():
        if server_is_on_subnet(subnet, server):
            hosts_in_subnet.append(server)

    return hosts_in_subnet


def servers_ips_on_subnet(conn, subnet):
    ips_in_subnet = []
    for server in conn.compute.servers():
        for network, network_attrs in server.addresses.items():
            ip_addresses = [x['addr'] for x in network_attrs]
            for ip in ip_addresses:
                if addr_in_subnet(subnet, ip):
                    ips_in_subnet.append(ip)

    return ips_in_subnet

def main():
    conn = initialize()
    manage_server, manage_ip = find_manage_server(conn)
    print(f'Management IP address: {manage_ip}')

    subnets = []
    for subnet in conn.network.subnets():
        subnets.append(subnet)

    print(servers_ips_on_subnet(conn, subnets[3]))

if __name__ == "__main__":
    main()
