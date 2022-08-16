def find_server_by_name(conn, name):
    for server in conn.compute.servers():
        if server.name == name:
            return server
    return None