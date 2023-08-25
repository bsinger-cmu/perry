#!/usr/bin/env python3
import time
import openstack 
import argparse
import sys

class OpenstackResetter():
    def __init__(self, conn) -> None:
        self.conn = conn
        self.current_index = 0

    def print_message(self, message,index = 1, total = 1, inc_cur = True):
        if (inc_cur):
            self.current_index += 1
        print(f"[RESET ({self.current_index}/{self.total_items})]\t({index}/{total})\t{message}...")

    def list_all(self):
        print(">---        Listing Openstack        ---<")
        self.initialize_lists()
        self.list_instances()
        self.list_floating_ips()
        self.list_routers()
        self.list_network_ports()
        self.list_subnets()
        self.list_networks()
        self.list_sec_groups()
        print(f"TOTAL ITEMS = {self.total_items}")
        print(">---            Finished!            ---<")

    def reset(self):
        print(">---       Resetting Openstack       ---<")
        self.initialize_lists()
        self.delete_instances()
        self.release_floating_ips()
        self.delete_routers()
        self.delete_network_ports()
        self.delete_subnets()
        self.delete_networks()
        self.delete_sec_groups()
        print(">---            Finished!            ---<")

    def initialize_lists(self):
        self.all_servers        = self.conn.list_servers()
        self.all_floating_ips   = self.conn.list_floating_ips()
        self.all_routers        = self.conn.list_routers()
        self.all_ports          = self.conn.list_ports()
        self.all_subnets        = self.conn.list_subnets()
        self.all_networks       = self.conn.list_networks()
        self.all_sec_groups     = self.conn.list_security_groups()
        self.total_instances    = len(self.all_servers)
        self.total_floating_ips = len(self.all_floating_ips)
        self.total_routers      = len(self.all_routers)
        self.total_ports        = len(self.all_ports)
        self.total_subnets      = len(self.all_subnets)
        self.total_networks     = len(self.all_networks)
        self.total_sec_groups   = len(self.all_sec_groups)
        self.total_items = self.total_instances + self.total_floating_ips + self.total_routers + self.total_ports + self.total_subnets + self.total_networks + self.total_sec_groups

    def list_instances(self):
        print("\nInstances:")
        for server in self.all_servers:
            print("[%s] - %s" % (server.id, server.name))

    def list_floating_ips(self):
        print("\nFloating IPs:")
        for ip in self.all_floating_ips:
            print("[%s] - %s (fixed: %s)" % (ip.id, ip.floating_ip_address, ip.fixed_ip_address))
    
    def list_interfaces(self, router):
        all_interfaces = self.conn.list_router_interfaces(router)
        print("> Interfaces:")
        for interface in all_interfaces:
            print("  * [%s] - %s" % (interface.id, interface.name))
            for fixed_ip in interface.fixed_ips:
                print("    ~ [%s] - Subnet Ip Address: %s" % (fixed_ip['subnet_id'], fixed_ip['ip_address']))

    def list_routers(self):
        print("\nRouters:")
        for router in self.all_routers:
            print("[%s] - %s" % (router.id, router.name))
            self.list_interfaces(router)

    def list_network_ports(self):
        print("\nPorts:")
        for port in self.all_ports:
            print("[%s] - %s" % (port.id, port.name))

    def list_subnets(self):
        print("\nSubnets:")
        for subnet in self.all_subnets:
            print("[%s] - %s" % (subnet.id, subnet.name))

    def list_networks(self):
        print("\nNetworks:")
        for network in self.all_networks:
            print("[%s] - %s" % (network.id, network.name))

    def list_sec_groups(self):
        print("\nSecurity Groups:")
        for sec_group in self.all_sec_groups:
            print("[%s] - %s" % (sec_group.id, sec_group.name))


    def delete_instances(self):
        current_server_index = 0
        for server in self.all_servers:
            current_server_index += 1
            self.print_message("Deleting instance %s" % server.name, current_server_index, self.total_instances)
            try:
                self.conn.delete_server(server.id)
            except Exception as e:
                print(f"Exception {e} in deleting instance {server.name}")
            time.sleep(0.1)

    def release_floating_ips(self):
        current_ip_index = 0
        for ip in self.all_floating_ips:
            current_ip_index += 1 
            message = "Releasing floating IP (floating: %s, fixed: %s)..." % (ip.floating_ip_address, ip.fixed_ip_address)
            self.print_message(message, current_ip_index, self.total_floating_ips)
            try:
                self.conn.delete_floating_ip(ip.id)
            except Exception as e:
                print(f"Exception {e} in releasing ip {ip.floating_ip_address}")
            time.sleep(0.1)

    def delete_interfaces(self, router):
        all_interfaces = self.conn.list_router_interfaces(router)
        current_interface_index = 0
        for interface in all_interfaces:
            current_interface_index += 1
            self.print_message("Deleting interface %s" % interface.id, current_interface_index, len(all_interfaces), False)
            for fixed_ip in interface.fixed_ips:
                try:
                    self.conn.remove_router_interface(router, subnet_id=fixed_ip['subnet_id'])
                except Exception as e:
                    print(f"Exception {e} in deleting interface {interface.id}")
                time.sleep(0.1)

    def delete_routers(self):
        current_router_index = 0
        for router in self.all_routers:
            current_router_index += 1
            self.print_message("Deleting router %s" % router.name, current_router_index, self.total_routers)
            try:
                self.delete_interfaces(router)
            except Exception as e:
                print(f"Exception {e} in deleting router {router.name}")
            self.conn.delete_router(router.id)
            time.sleep(0.1)

    def delete_network_ports(self):
        current_port_index = 0
        for port in self.all_ports:
            current_port_index += 1
            self.print_message("Deleting port %s" % port.name, current_port_index, self.total_ports)
            try:
                self.conn.delete_port(port.id)
            except Exception as e:
                print(f"Exception {e} in deleting port {port.id}")
            time.sleep(0.1)
    
    def delete_subnets(self):
        current_subnet_index = 0
        for subnet in self.all_subnets:
            current_subnet_index += 1
            self.print_message("Deleting subnet %s" % subnet.name, current_subnet_index, self.total_subnets)
            try:
                self.conn.delete_subnet(subnet.id)
            except Exception as e:
                print(f"Exception {e} in deleting subnet {subnet.name}")
            time.sleep(0.1)

    def delete_networks(self):
        current_network_index = 0
        for network in self.all_networks:
            current_network_index += 1
            if network.name == "external":
                self.print_message("Forbidden to delete network %s. Skipping" % network.name, current_network_index, self.total_networks)
                continue
            self.print_message("Deleting network %s" % network.name, current_network_index, self.total_networks)
            try:
                self.conn.delete_network(network.id)
            except Exception as e:
                print(f"Exception {e} in deleting network {network.name}")
            time.sleep(0.1)
    
    def delete_sec_groups(self):
        current_sec_group_index = 0
        for sec_group in self.all_sec_groups:
            current_sec_group_index += 1
            if sec_group.name == "default":
                self.print_message("Forbidden to delete security group %s. Skipping" % sec_group.name, current_sec_group_index, self.total_sec_groups)
                continue
            self.print_message("Deleting security group %s" % sec_group.name, current_sec_group_index, self.total_sec_groups)
            try:
                self.conn.delete_security_group(sec_group.id)
            except Exception as e:
                print(f"Exception {e} in deleting security group {sec_group.name}")
            time.sleep(0.1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Openstack resetter for when things go wrong and you need to start over.')
    parser.add_argument("-r", "--reset", help="Reset Openstack", action="store_true")
    parser.add_argument("-l", "--list", help="List Openstack resources", action="store_true")
    args = parser.parse_args()

    if not args.reset and not args.list:
        parser.print_help()
        sys.exit(1)
    conn = openstack.connect(cloud="default")
    opnstk = OpenstackResetter(conn)

    if args.reset:
        opnstk.reset()
    elif args.list:
        opnstk.list_all()
