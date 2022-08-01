from openstack_helper_functions.network_helpers import servers_ips_on_subnet

class AddHoneypot:
    def __init__(self, conn):
        self.conn = conn

    def create_keypair(self, keypair_name, ssh_dir='', private_keypair_file=''):
        keypair = self.conn.compute.find_keypair(keypair_name)

        if not keypair:
            print("Create Key Pair:")

            keypair = self.conn.compute.create_keypair(name=keypair_name)

            print(keypair)

            try:
                os.mkdir(ssh_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise e

            with open(private_keypair_file, 'w') as f:
                f.write("%s" % keypair.private_key)

            os.chmod(private_keypair_file, 0o400)

        return keypair

    def run(self, subnet, honeyname, port_name='eport2', private_keypair_file=''):
        print("Create Server:")
        image = self.conn.compute.find_image('cirros')#IMAGE_NAME
        flavor = self.conn.compute.find_flavor('m1.tiny')#FLAVOR_NAME
        network = self.conn.network.find_network('yn-flat')#FLAVOR_NAME
        keypair = self.create_keypair('microstack')

        #   Port 
        port = self.conn.network.find_port(port_name)
        print(port)

        server = self.conn.compute.create_server(
            name=honeyname, image_id=image.id, flavor_id=flavor.id,
            networks=[{"uuid": network.id}], key_name=keypair.name,
            port=port.id)

        server = self.conn.compute.wait_for_server(server)

        print("ssh -i {key} root@{ip}".format(
            key=private_keypair_file,
            ip=server.access_ipv4))

        # TODO: 
        
        #   Security group
        #   Install honeypot, etc
