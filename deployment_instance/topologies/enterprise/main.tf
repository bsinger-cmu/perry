######### Setup Networking #########
# External network is not managed by terraform, need to set as datasource
data "openstack_networking_network_v2" "external_network" {
  name = "external"
}

module "manage_rules" {
  source = "../modules/"
}

resource "openstack_networking_network_v2" "manage_network" {
  name           = "manage_network"
  admin_state_up = "true"
}

resource "openstack_networking_network_v2" "attacker_network" {
  name           = "attacker_network"
  admin_state_up = "true"
  description    = "The attacker network"
}

resource "openstack_networking_subnet_v2" "manage" {
  name            = "manage"
  network_id      = openstack_networking_network_v2.manage_network.id
  cidr            = "192.168.198.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_subnet_v2" "attacker_subnet" {
  name            = "attacker_network"
  network_id      = openstack_networking_network_v2.attacker_network.id
  cidr            = "192.168.202.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

# Root network
resource "openstack_networking_network_v2" "root_network" {
  name = "root_network"
}

variable "subnet_cidr" { default = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24", "10.0.4.0/24"] }
# Subnets for each branch (leaves)
resource "openstack_networking_subnet_v2" "subnets" {
  count           = 4
  name            = "branch-subnet-${count.index + 1}"
  network_id      = openstack_networking_network_v2.root_network.id
  cidr            = var.subnet_cidr[count.index]
  ip_version      = 4
  gateway_ip      = "10.0.${count.index + 1}.1"
  dns_nameservers = ["8.8.8.8"]
}

### Routers ###
resource "openstack_networking_router_v2" "router_external" {
  name                = "router_external"
  admin_state_up      = true
  external_network_id = data.openstack_networking_network_v2.external_network.id
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_external" {
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.manage.id
}

# Connect subnets
resource "openstack_networking_router_interface_v2" "router_interface_manage_company" {
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.router_interface.id
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_attacker" {
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.attacker_subnet.id
}


# Router to connect subnets
resource "openstack_networking_router_v2" "router" {
  name = "tree-topology-router"
}

resource "openstack_networking_router_interface_v2" "router_interface" {
  count     = 4
  router_id = openstack_networking_router_v2.router.id
  subnet_id = openstack_networking_subnet_v2.subnets[count.index].id
}

# Instances for leaf nodes
resource "openstack_compute_instance_v2" "leaf_nodes" {
  count       = 5
  name        = "leaf-node-${count.index + 1}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  network {
    uuid = openstack_networking_network_v2.root_network.id
  }
  security_groups = ["default", module.manage_rules.talk_to_manage_name]
}
