######### Setup Networking #########
# External network is not managed by terraform, need to set as datasource
data "openstack_networking_network_v2" "external_network" {
  name = "external"
}

resource "openstack_networking_network_v2" "manage_network" {
  name           = "manage_network"
  admin_state_up = "true"
}

resource "openstack_networking_network_v2" "attacker_network" {
  name           = "attacker_network"
  admin_state_up = "true"
}

resource "openstack_networking_network_v2" "network_A" {
  name           = "network_A"
  admin_state_up = "true"
}

resource "openstack_networking_network_v2" "network_B" {
  name           = "network_B"
  admin_state_up = "true"
}

resource "openstack_networking_network_v2" "flag_network" {
  name           = "flag_network"
  admin_state_up = "true"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "manage" {
  name       = "manage"
  network_id = "${openstack_networking_network_v2.manage_network.id}"
  cidr       = "192.168.198.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "subnet_attacker" {
  name       = "subnet_attacker"
  network_id = "${openstack_networking_network_v2.attacker_network.id}"
  cidr       = "192.168.200.0/24"
  ip_version = 4
}
resource "openstack_networking_subnet_v2" "subnet_A" {
  name       = "subnet_A"
  network_id = "${openstack_networking_network_v2.network_A.id}"
  cidr       = "192.168.201.0/24"
  ip_version = 4
}
resource "openstack_networking_subnet_v2" "subnet_B" {
  name       = "subnet_B"
  network_id = "${openstack_networking_network_v2.network_B.id}"
  cidr       = "192.168.202.0/24"
  ip_version = 4
}
resource "openstack_networking_subnet_v2" "subnet_flag" {
  name       = "subnet_flag"
  network_id = "${openstack_networking_network_v2.flag_network.id}"
  cidr       = "192.168.203.0/24"
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

resource "openstack_networking_secgroup_rule_v2" "tcp_all_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.simple.id}"
}

resource "openstack_networking_secgroup_rule_v2" "tcp_all_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.simple.id}"
}

resource "openstack_networking_secgroup_rule_v2" "udp_all_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.simple.id}"
}

resource "openstack_networking_secgroup_rule_v2" "udp_all_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 1
  port_range_max    = 65535
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

resource "openstack_networking_port_v2" "attacker_port" {
  name               = "attacker_port"
  network_id         = "${openstack_networking_network_v2.attacker_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.simple.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.subnet_attacker.id}"
    ip_address = "192.168.200.3"
  }
}

resource "openstack_networking_port_v2" "hostA_subnetA_port" {
  name               = "hostA_subnetA_port"
  network_id         = "${openstack_networking_network_v2.network_A.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.simple.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.subnet_A.id}"
    ip_address = "192.168.201.3"
  }
}

resource "openstack_networking_port_v2" "hostB_subnetB_port" {
  name               = "hostB_subnetB_port"
  network_id         = "${openstack_networking_network_v2.network_B.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.simple.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.subnet_B.id}"
    ip_address = "192.168.202.3"
  }
}

resource "openstack_networking_port_v2" "hostC_subnet_flag_port" {
  name               = "hostC_subnet_flag_port"
  network_id         = "${openstack_networking_network_v2.flag_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.simple.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.subnet_flag.id}"
    ip_address = "192.168.203.3"
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
resource "openstack_networking_router_interface_v2" "router_interface_manage_attacker" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.subnet_attacker.id}"
}
resource "openstack_networking_router_interface_v2" "router_interface_manage_subA" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.subnet_A.id}"
}
resource "openstack_networking_router_interface_v2" "router_interface_manage_subB" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.subnet_B.id}"
}
resource "openstack_networking_router_interface_v2" "router_interface_manage_sub_flag" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.subnet_flag.id}"
}

######### Setup Compute #########

### Management Host ###
resource "openstack_compute_instance_v2" "manage_host" {
  name            = "manage_host"
  image_name      = "Ubuntu20"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "cage"

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
resource "openstack_compute_instance_v2" "attacker_host" {
  name            = "attacker_host"
  image_name      = "Ubuntu20"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "cage"
  
  network {
    port = "${openstack_networking_port_v2.attacker_port.id}"
  }
}

resource "openstack_compute_instance_v2" "hostA" {
  name            = "hostA"
  image_name      = "Ubuntu20"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "cage"

  network {
    port = "${openstack_networking_port_v2.hostA_subnetA_port.id}"
  }
}

resource "openstack_compute_instance_v2" "hostB" {
  name            = "hostB"
  image_name      = "Ubuntu20"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "cage"

  network {
    port = "${openstack_networking_port_v2.hostB_subnetB_port.id}"
  }
}

resource "openstack_compute_instance_v2" "hostC" {
  name            = "hostC"
  image_name      = "Ubuntu20"
  flavor_name     = "m1.small"
  security_groups = ["${openstack_networking_secgroup_v2.simple.id}"]
  key_pair        = "cage"

  network {
    port = "${openstack_networking_port_v2.hostC_subnet_flag_port.id}"
  }
}