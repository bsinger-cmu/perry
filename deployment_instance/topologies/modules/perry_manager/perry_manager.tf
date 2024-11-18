# External network is not managed by terraform, need to set as datasource
data "openstack_networking_network_v2" "external_network" {
  name = "external"
}

output "external_network_id" {
  value = data.openstack_networking_network_v2.external_network.id
}

output "talk_to_manage_id" {
  value = openstack_networking_secgroup_v2.talk_to_manage.id
}

output "talk_to_manage_name" {
  value = openstack_networking_secgroup_v2.talk_to_manage.name
}

output "manage_freedom_id" {
  value = openstack_networking_secgroup_v2.manage_freedom.id
}
output "manage_freedom_name" {
  value = openstack_networking_secgroup_v2.manage_freedom.name
}

output "router_external_id" {
  value = openstack_networking_router_v2.router_external.id
}

### Management rules, all servers need SSH access from management network ###
resource "openstack_networking_secgroup_v2" "talk_to_manage" {
  name                 = "talk_to_manage"
  description          = ""
  delete_default_rules = true
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

# HTTPS
resource "openstack_networking_secgroup_rule_v2" "manage_https_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.talk_to_manage.id
}

resource "openstack_networking_secgroup_rule_v2" "manage_https_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.talk_to_manage.id
}

# Attacker
resource "openstack_networking_secgroup_rule_v2" "manage_attacker_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8888
  port_range_max    = 8888
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.talk_to_manage.id
}

resource "openstack_networking_secgroup_rule_v2" "manage_attacker_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8888
  port_range_max    = 8888
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.talk_to_manage.id
}

# Elasticsearch
resource "openstack_networking_secgroup_rule_v2" "manage_elasticsearch_in" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 9200
  port_range_max    = 9200
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.talk_to_manage.id
}
resource "openstack_networking_secgroup_rule_v2" "manage_elasticsearch_out" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 9200
  port_range_max    = 9200
  remote_ip_prefix  = "0.0.0.0/0"
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

resource "openstack_networking_router_v2" "router_external" {
  name                = "router_external"
  admin_state_up      = true
  external_network_id = data.openstack_networking_network_v2.external_network.id
}
