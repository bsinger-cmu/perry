### Management rules, all servers need SSH access from management network ###
resource "openstack_networking_secgroup_v2" "talk_to_manage" {
  name        = "talk_to_manage"
  description = ""
}

resource "openstack_networking_secgroup_rule_v2" "manage_ssh_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "192.168.198.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.talk_to_manage.id}"
}

resource "openstack_networking_secgroup_rule_v2" "manage_ssh_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "192.168.198.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.talk_to_manage.id}"
}

resource "openstack_networking_secgroup_v2" "manage_freedom" {
  name        = "manage_freedom"
  description = ""
}

resource "openstack_networking_secgroup_rule_v2" "manage_freedom" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.manage_freedom.id}"
}

resource "openstack_networking_secgroup_rule_v2" "manage_freedom_ssh_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.manage_freedom.id}"
}
resource "openstack_networking_secgroup_rule_v2" "manage_freedom_ssh_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.manage_freedom.id}"
}

### Company Network Rules ###
resource "openstack_networking_secgroup_v2" "company" {
  name        = "company"
  description = "Company security group"
}
# Company Network talks to Datacenter Network
resource "openstack_networking_secgroup_rule_v2" "tcp_in_datacenter" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.company.id}"
}
resource "openstack_networking_secgroup_rule_v2" "tcp_out_datacenter" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.company.id}"
}

### Datacenter Network Rules ###
resource "openstack_networking_secgroup_v2" "datacenter" {
  name        = "datacenter"
  description = "datacenter security group"
}

# Datacenter Network talks to Company Network
resource "openstack_networking_secgroup_rule_v2" "tcp_in_company" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.datacenter.id}"
}
resource "openstack_networking_secgroup_rule_v2" "tcp_out_company" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.datacenter.id}"
}