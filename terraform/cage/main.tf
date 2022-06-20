######### Setup Networking #########
# External network is not managed by terraform, need to set as datasource
data "openstack_networking_network_v2" "external_network" {
  name = "external"
}

resource "openstack_networking_network_v2" "manage_network" {
  name           = "manage_network"
  admin_state_up = "true"
}

resource "openstack_networking_network_v2" "internal_network" {
  name           = "internal_network"
  admin_state_up = "true"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "manage" {
  name       = "manage"
  network_id = "${openstack_networking_network_v2.manage_network.id}"
  cidr       = "192.168.198.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "internal_subnet1" {
  name       = "subnet_manage"
  network_id = "${openstack_networking_network_v2.internal_network.id}"
  cidr       = "192.168.199.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "internal_subnet2" {
  name       = "subnet_manage"
  network_id = "${openstack_networking_network_v2.internal_network.id}"
  cidr       = "192.168.200.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "internal_subnet3" {
  name       = "subnet_manage"
  network_id = "${openstack_networking_network_v2.internal_network.id}"
  cidr       = "192.168.201.0/24"
  ip_version = 4
}


### Security Groups ###
resource "openstack_networking_secgroup_v2" "simple" {
  name        = "simple"
  description = ""
}

resource "openstack_networking_secgroup_rule_v2" "icmp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.simple.id}"
}

resource "openstack_networking_secgroup_rule_v2" "icmp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.simple.id}"
}

resource "openstack_networking_secgroup_rule_v2" "ssh_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.simple.id}"
}

resource "openstack_networking_secgroup_rule_v2" "ssh_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.simple.id}"
}

### Ports ###
# Host Ports
resource "openstack_networking_port_v2" "manage_port_host" {
  name               = "manage_port_host"
  network_id         = "${openstack_networking_network_v2.manage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.simple.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.manage.id}"
  }
}

resource "openstack_networking_port_v2" "port_sub1_host1" {
  name               = "port_sub1_host1"
  network_id         = "${openstack_networking_network_v2.internal_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.simple.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.internal_subnet1.id}"
    ip_address = "192.168.199.3"
  }
}

resource "openstack_networking_port_v2" "port_sub2_host1" {
  name               = "port_sub2_host1"
  network_id         = "${openstack_networking_network_v2.internal_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.simple.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.internal_subnet2.id}"
    ip_address = "192.168.200.3"
  }
}

resource "openstack_networking_port_v2" "port_sub3_host1" {
  name               = "port_sub3_host1"
  network_id         = "${openstack_networking_network_v2.internal_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.simple.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.internal_subnet3.id}"
    ip_address = "192.168.201.3"
  }
}

### Routers ###
resource "openstack_networking_router_v2" "router_external" {
  name                = "router_external"
  admin_state_up      = true
  external_network_id = "${data.openstack_networking_network_v2.external_network.id}"
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_external" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.manage.id}"
}

# Connect subnets
resource "openstack_networking_router_interface_v2" "router_interface_manage_sub1" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.internal_subnet1.id}"
}
resource "openstack_networking_router_interface_v2" "router_interface_manage_sub2" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.internal_subnet2.id}"
}
resource "openstack_networking_router_interface_v2" "router_interface_manage_sub3" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.internal_subnet3.id}"
}

######### Setup Compute #########

### Management Host ###
resource "openstack_compute_instance_v2" "manage_host" {
  name            = "manage_host"
  image_name      = "Ubuntu18"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "microstack"

  network {
    port = "${openstack_networking_port_v2.manage_port_host.id}"
  }
}

resource "openstack_networking_floatingip_v2" "manage_floating_ip" {
  pool = "external"
}

resource "openstack_networking_floatingip_associate_v2" "fip_manage" {
  floating_ip = "${openstack_networking_floatingip_v2.manage_floating_ip.address}"
  port_id = "${openstack_networking_port_v2.manage_port_host.id}"
}

### Subnet 1 Hosts ###
resource "openstack_compute_instance_v2" "sub1_host1" {
  name            = "sub1_host1"
  image_name      = "Ubuntu18"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "microstack"

  network {
    port = "${openstack_networking_port_v2.port_sub1_host1.id}"
  }
}

resource "openstack_compute_instance_v2" "sub2_host1" {
  name            = "sub2_host1"
  image_name      = "Ubuntu18"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "microstack"

  network {
    port = "${openstack_networking_port_v2.port_sub2_host1.id}"
  }
}

resource "openstack_compute_instance_v2" "sub3_host1" {
  name            = "sub3_host1"
  image_name      = "Ubuntu18"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "microstack"

  network {
    port = "${openstack_networking_port_v2.port_sub3_host1.id}"
  }
}