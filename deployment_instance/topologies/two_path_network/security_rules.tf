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

### Attacker Network rules ###
# Attacker network can only talk to network A or network B
resource "openstack_networking_secgroup_v2" "attacker" {
  name        = "attacker"
  description = ""
}
# A
resource "openstack_networking_secgroup_rule_v2" "attacker_tcp_in_A" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.attacker.id}"
}
resource "openstack_networking_secgroup_rule_v2" "attacker_tcp_out_A" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.attacker.id}"
}
# B
resource "openstack_networking_secgroup_rule_v2" "attacker_tcp_in_B" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.202.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.attacker.id}"
}
resource "openstack_networking_secgroup_rule_v2" "attacker_tcp_out_B" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.202.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.attacker.id}"
}

### Network A rules ###
# A can only talk to attacker network or flag network
resource "openstack_networking_secgroup_v2" "A" {
  name        = "A"
  description = ""
}
# Attacker
resource "openstack_networking_secgroup_rule_v2" "A_tcp_in_attacker" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.A.id}"
}
resource "openstack_networking_secgroup_rule_v2" "A_tcp_out_attacker" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.A.id}"
}
# Flag
resource "openstack_networking_secgroup_rule_v2" "A_tcp_in_flag" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.203.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.A.id}"
}
resource "openstack_networking_secgroup_rule_v2" "A_tcp_out_flag" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.203.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.A.id}"
}

### Network B rules ###
# B can only talk to attacker network or flag network
resource "openstack_networking_secgroup_v2" "B" {
  name        = "B"
  description = ""
}
# Attacker
resource "openstack_networking_secgroup_rule_v2" "B_tcp_in_attacker" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.B.id}"
}
resource "openstack_networking_secgroup_rule_v2" "B_tcp_out_attacker" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.B.id}"
}
# Flag
resource "openstack_networking_secgroup_rule_v2" "B_tcp_in_flag" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.203.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.B.id}"
}
resource "openstack_networking_secgroup_rule_v2" "B_tcp_out_flag" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.203.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.B.id}"
}

### Flag network rules, only talk to network A or network B ###
resource "openstack_networking_secgroup_v2" "flag" {
  name        = "flag"
  description = ""
}
# A
resource "openstack_networking_secgroup_rule_v2" "tcp_in_A" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.flag.id}"
}
resource "openstack_networking_secgroup_rule_v2" "tcp_out_A" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.flag.id}"
}
# B
resource "openstack_networking_secgroup_rule_v2" "tcp_in_B" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.202.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.flag.id}"
}
resource "openstack_networking_secgroup_rule_v2" "tcp_out_B" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.202.0/24"
  security_group_id = "${openstack_networking_secgroup_v2.flag.id}"
}
