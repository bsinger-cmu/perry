def find_server_by_name(conn, name):
    for server in conn.compute.servers():
        if server.name == name:
            return server
    return None


def find_server_by_ip(conn, ip):
    for server in conn.compute.servers():
        for network, network_attrs in server.addresses.items():
            ip_addresses = [x["addr"] for x in network_attrs]
            if ip in ip_addresses:
                return server
    return None


def shutdown_server_by_name(conn, name):
    server = find_server_by_name(conn, name)
    if server:
        conn.compute.stop_server(server)
        return True
    return False


def shutdown_server_by_ip(conn, ip):
    server = find_server_by_ip(conn, ip)
    if server:
        conn.compute.stop_server(server)
        return True
    return False
