#!/usr/bin/env python3
import openstack 
import argparse
import sys

class OpenstackResetter():
    def __init__(self, conn) -> None:
        self.conn = conn

    def print_message(self, message, index = 1, total = 1):
        print("[RESET]\t(%d/%d)\t%s..." % (index, total, message))

    def list_all(self):
        self.list_instances()
        self.list_floating_ips()
        self.list_routers()
        self.list_network_ports()
        self.list_subnets()
        self.list_networks()
        self.list_sec_groups()

    def reset(self):
        self.print_message("Resetting Openstack")
        self.delete_instances()
        self.release_floating_ips()
        self.delete_routers()
        self.delete_network_ports()
        self.delete_subnets()
        self.delete_networks()
        self.delete_sec_groups()
        self.print_message("Finished!")

    def list_instances(self):
        all_servers = self.conn.list_servers()
        print("")
        print("Instances:")
        for server in all_servers:
            print("[%s] - %s" % (server.id, server.name))

    def list_floating_ips(self):
        all_floating_ips = self.conn.list_floating_ips()
        print("")
        print("Floating IPs:")
        for ip in all_floating_ips:
            print("[%s] - %s (fixed: %s)" % (ip.id, ip.floating_ip_address, ip.fixed_ip_address))
    
    def list_interfaces(self, router):
        all_interfaces = self.conn.list_router_interfaces(router)
        print("> Interfaces:")
        for interface in all_interfaces:
            print("  * [%s] - %s" % (interface.id, interface.name))
            for fixed_ip in interface.fixed_ips:
                print("    ~ [%s] - Subnet Ip Address: %s" % (fixed_ip['subnet_id'], fixed_ip['ip_address']))

    def list_routers(self):
        all_routers = self.conn.list_routers()
        print("")
        print("Routers:")
        for router in all_routers:
            print("[%s] - %s" % (router.id, router.name))
            self.list_interfaces(router)

    def list_network_ports(self):
        all_ports = self.conn.list_ports()
        print("")
        print("Ports:")
        for port in all_ports:
            print("[%s] - %s" % (port.id, port.name))

    def list_subnets(self):
        all_subnets = self.conn.list_subnets()
        print("")
        print("Subnets:")
        for subnet in all_subnets:
            print("[%s] - %s" % (subnet.id, subnet.name))

    def list_networks(self):
        all_networks = self.conn.list_networks()
        print("")
        print("Networks:")
        for network in all_networks:
            print("[%s] - %s" % (network.id, network.name))

    def list_sec_groups(self):
        all_sec_groups = self.conn.list_security_groups()
        print("")
        print("Security Groups:")
        for sec_group in all_sec_groups:
            print("[%s] - %s" % (sec_group.id, sec_group.name))


    def delete_instances(self):
        all_servers = self.conn.list_servers()
        current_server_index = 0
        for server in all_servers:
            current_server_index += 1
            self.print_message("Deleting instance %s" % server.name, current_server_index, len(all_servers))
            self.conn.delete_server(server.id)

    def release_floating_ips(self):
        all_floating_ips = self.conn.list_floating_ips()
        current_ip_index = 0
        for ip in all_floating_ips:
            current_ip_index += 1 
            message = "Releasing floating IP (floating: %s, fixed: %s)..." % (ip.floating_ip_address, ip.fixed_ip_address)
            self.print_message(message, current_ip_index, len(all_floating_ips))
            self.conn.delete_floating_ip(ip.id)

    def delete_interfaces(self, router):
        all_interfaces = self.conn.list_router_interfaces(router)
        current_interface_index = 0
        for interface in all_interfaces:
            current_interface_index += 1
            self.print_message("Deleting interface %s" % interface.id, current_interface_index, len(all_interfaces))
            for fixed_ip in interface.fixed_ips:
                self.conn.remove_router_interface(router, subnet_id=fixed_ip['subnet_id'])

    def delete_routers(self):
        all_routers = self.conn.list_routers()
        current_router_index = 0
        for router in all_routers:
            current_router_index += 1
            self.print_message("Deleting router %s" % router.name, current_router_index, len(all_routers))
            self.delete_interfaces(router)
            self.conn.delete_router(router.id)

    def delete_network_ports(self):
        all_ports = self.conn.list_ports()
        current_port_index = 0
        for port in all_ports:
            current_port_index += 1
            self.print_message("Deleting port %s" % port.name, current_port_index, len(all_ports))
            self.conn.delete_port(port.id)
    
    def delete_subnets(self):
        all_subnets = self.conn.list_subnets()
        current_subnet_index = 0
        for subnet in all_subnets:
            current_subnet_index += 1
            self.print_message("Deleting subnet %s" % subnet.name, current_subnet_index, len(all_subnets))
            self.conn.delete_subnet(subnet.id)

    def delete_networks(self):
        all_networks = self.conn.list_networks()
        current_network_index = 0
        for network in all_networks:
            current_network_index += 1
            if network.name == "external":
                self.print_message("Forbidden to delete network %s. Skipping" % network.name, current_network_index, len(all_networks))
                continue
            self.print_message("Deleting network %s" % network.name, current_network_index, len(all_networks))
            self.conn.delete_network(network.id)
    
    def delete_sec_groups(self):
        all_sec_groups = self.conn.list_security_groups()
        current_sec_group_index = 0
        for sec_group in all_sec_groups:
            current_sec_group_index += 1
            if sec_group.name == "default":
                self.print_message("Forbidden to delete security group %s. Skipping" % sec_group.name, current_sec_group_index, len(all_sec_groups))
                continue
            self.print_message("Deleting security group %s" % sec_group.name, current_sec_group_index, len(all_sec_groups))
            self.conn.delete_security_group(sec_group.id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Openstack resetter for when things go wrong and you need to start over.')
    parser.add_argument("-r", "--reset", help="Reset Openstack", action="store_true")
    parser.add_argument("-l", "--list", help="List Openstack resources", action="store_true")
    args = parser.parse_args()

    if not args.reset and not args.list:
        parser.print_help()
        sys.exit(1)
    conn = openstack.connect(cloud="default")
    opnstk = OpenstackResetter()

    if args.reset:
        opnstk.reset()
    elif args.list:
        opnstk.list_all()
