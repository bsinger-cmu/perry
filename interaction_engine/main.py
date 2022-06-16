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
                    return server

def main():
    conn = initialize()
    find_manage_server(conn)

if __name__=="__main__":
    main()