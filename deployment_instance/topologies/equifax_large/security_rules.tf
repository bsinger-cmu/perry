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

### Webserver Network Rules ###
resource "openstack_networking_secgroup_v2" "webserver" {
  name        = "webserver"
  description = "Webserver security group"
}

# Webservers can talk to anything
resource "openstack_networking_secgroup_rule_v2" "webserver_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.webserver.id
}
resource "openstack_networking_secgroup_rule_v2" "webserver_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.webserver.id
}


### Critical Company Network Rules ###
resource "openstack_networking_secgroup_v2" "critical_company" {
  name        = "critical_company"
  description = "critical company security group"
}

# Everyone in critical company can talk to each other
resource "openstack_networking_secgroup_rule_v2" "intra_critical_company_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = openstack_networking_secgroup_v2.critical_company.id
}

resource "openstack_networking_secgroup_rule_v2" "intra_critical_company_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.201.0/24"
  security_group_id = openstack_networking_secgroup_v2.critical_company.id
}

resource "openstack_networking_secgroup_rule_v2" "critical_company_webserver_tcp_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = openstack_networking_secgroup_v2.critical_company.id
}

resource "openstack_networking_secgroup_rule_v2" "critical_company_webserver_tcp_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1
  port_range_max    = 65535
  remote_ip_prefix  = "192.168.200.0/24"
  security_group_id = openstack_networking_secgroup_v2.critical_company.id
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


