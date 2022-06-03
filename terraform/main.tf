######### Setup Networking #########
resource "openstack_networking_network_v2" "cage_network" {
  name           = "cage_network"
  admin_state_up = "true"
}

### Subnets ###
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
resource "openstack_compute_secgroup_v2" "ssh_group" {
  name        = "ssh_group"
  description = "SSH Security Group"

  rule {
    from_port   = 22
    to_port     = 22
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }
}

resource "openstack_networking_port_v2" "cage_sub1_port1" {
  name               = "sub1_port1"
  network_id         = "${openstack_networking_network_v2.cage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_compute_secgroup_v2.ssh_group.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.cage_subnet_1.id}"
    ip_address = "192.168.199.10"
  }
}

resource "openstack_networking_port_v2" "cage_sub2_port1" {
  name               = "sub2_port1"
  network_id         = "${openstack_networking_network_v2.cage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_compute_secgroup_v2.ssh_group.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.cage_subnet_2.id}"
    ip_address = "192.168.200.10"
  }
}

resource "openstack_networking_port_v2" "cage_sub3_port1" {
  name               = "sub3_port1"
  network_id         = "${openstack_networking_network_v2.cage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_compute_secgroup_v2.ssh_group.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.cage_subnet_3.id}"
    ip_address = "192.168.201.10"
  }
}

######### Setup Compute #########

#### Setup Hosts in Subnet 1 ###
resource "openstack_compute_instance_v2" "test" {
  name            = "test-vm"
  image_name      = "cirros"
  flavor_name     = "m1.tiny"
  security_groups = ["ssh_group"]

  network {
    port = "${openstack_networking_port_v2.cage_sub1_port1.id}"
  }
}