from actions.simpleScan import SimpleScan
import openstack


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


def main():
    conn = initialize()
    manage_server, manage_ip = find_manage_server(conn)
    print(f'Management IP address: {manage_ip}')

    subnets = []
    for subnet in conn.network.subnets():
        subnets.append(subnet)

    scanner = SimpleScan(conn)
    print(scanner.run(subnets[3]))

if __name__ == "__main__":
    main()
