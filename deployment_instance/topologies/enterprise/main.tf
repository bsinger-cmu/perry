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

resource "openstack_networking_network_v2" "root_network" {
  count = 4
  name  = "root-network-${count.index + 1}"
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

# 1 subnet for each branch
variable "subnet_cidr" { default = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24", "10.0.4.0/24"] }
resource "openstack_networking_subnet_v2" "subnets" {
  count           = 4
  name            = "branch-subnet-${count.index + 1}"
  network_id      = openstack_networking_network_v2.root_network[count.index].id
  cidr            = "10.0.${count.index + 1}.0/24"
  ip_version      = 4
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
resource "openstack_networking_router_interface_v2" "router_interface_manage_attacker" {
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.attacker_subnet.id
}


# Router to connect subnets
resource "openstack_networking_router_interface_v2" "router_interface" {
  count     = 4
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.subnets[count.index].id
}

# Instances for leaf nodes
resource "openstack_compute_instance_v2" "br1_leaf_nodes" {
  count       = 5
  name        = "br1-node-${count.index + 1}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  network {
    uuid        = openstack_networking_network_v2.root_network.id
    fixed_ip_v4 = "10.0.1.${count.index + 10}"
  }
  security_groups = ["default", module.manage_rules.talk_to_manage_name]
  depends_on      = [openstack_networking_subnet_v2.subnets, openstack_networking_network_v2.root_network]
}

resource "openstack_compute_instance_v2" "br2_leaf_nodes" {
  count       = 5
  name        = "br2-node-${count.index + 1}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  network {
    uuid        = openstack_networking_network_v2.root_network.id
    fixed_ip_v4 = "10.0.2.${count.index + 10}"
  }
  security_groups = ["default", module.manage_rules.talk_to_manage_name]
  depends_on      = [openstack_networking_subnet_v2.subnets, openstack_compute_instance_v2.br1_leaf_nodes, openstack_networking_network_v2.root_network]
}

resource "openstack_compute_instance_v2" "br3_leaf_nodes" {
  count       = 5
  name        = "br3-node-${count.index + 1}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  network {
    uuid        = openstack_networking_network_v2.root_network.id
    fixed_ip_v4 = "10.0.3.${count.index + 10}"
  }
  security_groups = ["default", module.manage_rules.talk_to_manage_name]
  depends_on      = [openstack_networking_subnet_v2.subnets, openstack_networking_network_v2.root_network, openstack_compute_instance_v2.br2_leaf_nodes]
}

resource "openstack_compute_instance_v2" "br4_leaf_nodes" {
  count       = 5
  name        = "br4-node-${count.index + 1}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  network {
    uuid        = openstack_networking_network_v2.root_network.id
    fixed_ip_v4 = "10.0.4.${count.index + 10}"
  }
  security_groups = ["default", module.manage_rules.talk_to_manage_name]
  depends_on      = [openstack_networking_subnet_v2.subnets, openstack_compute_instance_v2.br3_leaf_nodes, openstack_networking_network_v2.root_network]
}

resource "openstack_compute_instance_v2" "manage_host" {
  name        = "manage_host"
  image_name  = "Ubuntu20"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    module.manage_rules.talk_to_manage_name,
    module.manage_rules.manage_freedom_name
  ]

  network {
    name = "manage_network"
  }
  depends_on = [openstack_networking_subnet_v2.manage]
}

resource "openstack_networking_floatingip_v2" "manage_floating_ip" {
  pool = "external"
}

resource "openstack_compute_floatingip_associate_v2" "fip_manage" {
  floating_ip = openstack_networking_floatingip_v2.manage_floating_ip.address
  instance_id = openstack_compute_instance_v2.manage_host.id
}
