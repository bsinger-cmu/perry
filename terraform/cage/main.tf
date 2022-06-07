######### Setup Networking #########
resource "openstack_networking_network_v2" "cage_network" {
  name           = "cage_network"
  admin_state_up = "true"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "cage_subnet_manage" {
  name       = "cage_subnet_manage"
  network_id = "${openstack_networking_network_v2.cage_network.id}"
  cidr       = "192.168.198.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "cage_subnet_1" {
  name       = "cage_subnet_1"
  network_id = "${openstack_networking_network_v2.cage_network.id}"
  cidr       = "192.168.199.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "cage_subnet_2" {
  name       = "cage_subnet_2"
  network_id = "${openstack_networking_network_v2.cage_network.id}"
  cidr       = "192.168.200.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "cage_subnet_3" {
  name       = "cage_subnet_3"
  network_id = "${openstack_networking_network_v2.cage_network.id}"
  cidr       = "192.168.201.0/24"
  ip_version = 4
}

### Security Groups ###
resource "openstack_networking_secgroup_v2" "ssh_group" {
  name        = "cage_ssh_group"
  description = "SSH Security Group"
}

resource "openstack_networking_secgroup_rule_v2" "ssh_rule_1" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.ssh_group.id}"
}

resource "openstack_networking_secgroup_rule_v2" "ssh_rule_2" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.ssh_group.id}"
}

### Management Network ###
# TODO external network id can change, we should automate this
# resource "openstack_networking_router_v2" "router_manage" {
#   name                = "router_manage"
#   admin_state_up      = true
#   external_network_id = "521fbd30-9e6f-49cc-b687-24b8bc3e4292"
#   #external_network_id = "${openstack_networking_network_v2.cage_network_external.id}"
# }

resource "openstack_networking_port_v2" "cage_manage_port_host" {
  name               = "manage_port_host"
  network_id         = "${openstack_networking_network_v2.cage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.ssh_group.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.cage_subnet_manage.id}"
    ip_address = "192.168.198.3"
  }
}

resource "openstack_networking_port_v2" "cage_manage_port_router" {
  name               = "manage_port_router"
  network_id         = "${openstack_networking_network_v2.cage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.ssh_group.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.cage_subnet_manage.id}"
    ip_address = "192.168.198.4"
  }
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_external" {
  router_id = "d3788cdd-797c-4bd3-8870-1ea49d93b768"
  subnet_id = "eb9743a4-6b0e-4f2c-b2da-b980fde6d90b"
}
resource "openstack_networking_router_interface_v2" "router_interface_manage_internal" {
  router_id = "d3788cdd-797c-4bd3-8870-1ea49d93b768"
  port_id = "${openstack_networking_port_v2.cage_manage_port_router.id}"
}


### Ports ###
resource "openstack_networking_port_v2" "cage_sub1_port1" {
  name               = "sub1_port1"
  network_id         = "${openstack_networking_network_v2.cage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.ssh_group.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.cage_subnet_1.id}"
    ip_address = "192.168.199.10"
  }
}

resource "openstack_networking_port_v2" "cage_sub2_port1" {
  name               = "sub2_port1"
  network_id         = "${openstack_networking_network_v2.cage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.ssh_group.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.cage_subnet_2.id}"
    ip_address = "192.168.200.10"
  }
}

resource "openstack_networking_port_v2" "cage_sub3_port1" {
  name               = "sub3_port1"
  network_id         = "${openstack_networking_network_v2.cage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.ssh_group.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.cage_subnet_3.id}"
    ip_address = "192.168.201.10"
  }
}

######### Setup Compute #########

### Management Host ###
resource "openstack_compute_instance_v2" "manage_host" {
  name            = "cage_manage"
  image_name      = "Ubuntu18"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.ssh_group.id}"]
  key_pair        = "microstack"

  network {
    port = "${openstack_networking_port_v2.cage_manage_port_host.id}"
  }
}

resource "openstack_compute_floatingip_v2" "manage_floating_ip" {
  pool = "external"
}

resource "openstack_compute_floatingip_associate_v2" "fip_manage" {
  floating_ip = "${openstack_compute_floatingip_v2.manage_floating_ip.address}"
  instance_id = "${openstack_compute_instance_v2.manage_host.id}"
}

# resource "openstack_compute_instance_v2" "gateway" {
#   name            = "cage_gateway"
#   image_name      = "Ubuntu18"
#   flavor_name     = "m1.small"
#   security_groups = ["ssh_group"]

#   network {
#     name = "${openstack_networking_network_v2.cage_network.name}"
#   }
# }

#### Setup Hosts in Subnet 1 ###
# resource "openstack_compute_instance_v2" "sub1_host1" {
#   name            = "cage_sub1_host1"
#   image_name      = "Ubuntu18"
#   flavor_name     = "m1.small"
#   security_groups = ["ssh_group"]

#   network {
#     port = "${openstack_networking_port_v2.cage_sub1_port1.id}"
#   }
# }