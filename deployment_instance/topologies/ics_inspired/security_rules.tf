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
  security_group_id = openstack_networking_secgroup_v2.talk_to_manage.id
}

resource "openstack_networking_secgroup_rule_v2" "manage_ssh_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "192.168.198.0/24"
  security_group_id = openstack_networking_secgroup_v2.talk_to_manage.id
}
resource "openstack_networking_secgroup_v2" "manage_freedom" {
  name        = "manage_freedom"
  description = ""
}

resource "openstack_networking_secgroup_rule_v2" "manage_freedom_ssh_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.manage_freedom.id
}
resource "openstack_networking_secgroup_rule_v2" "manage_freedom_ssh_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.manage_freedom.id
}

### Employee One Network Rules ###
resource "openstack_networking_secgroup_v2" "employee_one_group" {
  name        = "employee_one_group"
  description = "employee one security group"
}

# Employee One can talk to anything
resource "openstack_networking_secgroup_rule_v2" "employee_one_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.employee_one_group.id
}
resource "openstack_networking_secgroup_rule_v2" "employee_one_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.employee_one_group.id
}

### Employee Two Network Rules ###
resource "openstack_networking_secgroup_v2" "employee_two_group" {
  name        = "employee_two_group"
  description = "employee two security group"
}

# Employee Two can talk to anything
resource "openstack_networking_secgroup_rule_v2" "employee_two_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.employee_two_group.id
}

resource "openstack_networking_secgroup_rule_v2" "employee_two_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.employee_two_group.id
}


### OT Network ###
resource "openstack_networking_secgroup_v2" "ot_group" {
  name        = "ot_group"
  description = "OT network security group"
}

# OT can only talk to Employee One and Employee Two and the management network
resource "openstack_networking_secgroup_rule_v2" "ot_employee_one_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = openstack_networking_secgroup_v2.ot_group.id
}

resource "openstack_networking_secgroup_rule_v2" "ot_employee_two_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = openstack_networking_secgroup_v2.ot_group.id
}

resource "openstack_networking_secgroup_rule_v2" "intra_ot_network" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.203.0/24"
  security_group_id = openstack_networking_secgroup_v2.ot_group.id
}

resource "openstack_networking_secgroup_rule_v2" "ot_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.ot_group.id
}

### Attacker Network Rules ###
resource "openstack_networking_secgroup_v2" "attacker" {
  name        = "attacker"
  description = "attacker security group"
}

# Attackers can talk to anything
resource "openstack_networking_secgroup_rule_v2" "attacker_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.attacker.id
}

resource "openstack_networking_secgroup_rule_v2" "attacker_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.attacker.id
}


