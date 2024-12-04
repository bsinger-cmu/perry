######### Setup Networking #########
module "perry_manager" {
  source   = "../modules/perry_manager"
  key_name = var.perry_key_name
}

module "attacker" {
  source             = "../modules/attacker"
  router_external_id = module.perry_manager.router_external_id
  key_name           = var.perry_key_name
}

resource "openstack_networking_network_v2" "dev_network" {
  name           = "dev_network"
  admin_state_up = "true"
  description    = "The dev network"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "dev_subnet" {
  name            = "dev_network"
  network_id      = openstack_networking_network_v2.dev_network.id
  cidr            = "192.168.200.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

### Routers ###
# Connect subnets
resource "openstack_networking_router_interface_v2" "router_interface_manage_company" {
  router_id = module.perry_manager.router_external_id
  subnet_id = openstack_networking_subnet_v2.dev_subnet.id
}

######### Setup Compute #########
### Webserver Subnet Hosts ###
resource "openstack_compute_instance_v2" "host" {
  count       = 3
  name        = "host_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.perry_manager.talk_to_manage_name,
    openstack_networking_secgroup_v2.dev_hosts.name
  ]

  network {
    name = "dev_network"
    // sequential ips
    fixed_ip_v4 = "192.168.200.${count.index + 10}"
  }

  depends_on = [openstack_networking_subnet_v2.dev_subnet]
}
