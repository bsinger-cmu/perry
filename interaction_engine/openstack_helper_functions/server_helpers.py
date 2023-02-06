def find_server_by_name(conn, name):
    for server in conn.compute.servers():
        if server.name == name:
            return server
    return None

def shutdown_server_by_name(conn, name):
    server = find_server_by_name(conn, name)
    if server:
        conn.compute.stop_server(server)
        return True
    return False