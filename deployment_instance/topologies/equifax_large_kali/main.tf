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

resource "openstack_networking_network_v2" "webserver_network" {
  name           = "webserver_network"
  admin_state_up = "true"
  description    = "The external webserver network"
}

resource "openstack_networking_network_v2" "critical_company_network" {
  name           = "critical_company_network"
  admin_state_up = "true"
  description    = "The corporate network with critical data"
}

resource "openstack_networking_network_v2" "attacker_network" {
  name           = "attacker_network"
  admin_state_up = "true"
  description    = "The attacker network"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "manage" {
  name            = "manage"
  network_id      = openstack_networking_network_v2.manage_network.id
  cidr            = "192.168.198.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_subnet_v2" "webserver_subnet" {
  name            = "webserver_network"
  network_id      = openstack_networking_network_v2.webserver_network.id
  cidr            = "192.168.200.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

resource "openstack_networking_subnet_v2" "critical_company_subnet" {
  name            = "critical_company_network"
  network_id      = openstack_networking_network_v2.critical_company_network.id
  cidr            = "192.168.201.0/24"
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
resource "openstack_networking_router_interface_v2" "router_interface_manage_company" {
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.webserver_subnet.id
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_datacenter" {
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.critical_company_subnet.id
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_attacker" {
  router_id = openstack_networking_router_v2.router_external.id
  subnet_id = openstack_networking_subnet_v2.attacker_subnet.id
}

######### Setup Compute #########

### Management Host ###
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

### Webserver Subnet Hosts ###
resource "openstack_compute_instance_v2" "webserver" {
  count       = 2
  name        = "webserver_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.manage_rules.talk_to_manage_name,
    openstack_networking_secgroup_v2.webserver.name
  ]

  network {
    name = "webserver_network"
    // sequential ips
    fixed_ip_v4 = "192.168.200.${count.index + 10}"
  }

  depends_on = [openstack_networking_subnet_v2.webserver_subnet]
}

### Corporate Subnet Hosts ###
resource "openstack_compute_instance_v2" "employee" {
  count       = 0
  name        = "employee_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.manage_rules.talk_to_manage_name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "critical_company_network"
    fixed_ip_v4 = "192.168.201.${count.index + 10}"
  }

  depends_on = [openstack_networking_subnet_v2.critical_company_subnet]
}

resource "openstack_compute_instance_v2" "database" {
  count       = 48
  name        = "database_${count.index}"
  image_name  = "Ubuntu20"
  flavor_name = "p2.tiny"
  key_pair    = var.perry_key_name
  security_groups = [
    module.manage_rules.talk_to_manage_name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "critical_company_network"
    fixed_ip_v4 = "192.168.201.${count.index + 50}"
  }

  depends_on = [openstack_networking_subnet_v2.critical_company_subnet]
}

### Attacker Subnet Hosts ###
resource "openstack_compute_instance_v2" "attacker" {
  name        = "attacker"
  image_name  = "Kali"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    module.manage_rules.talk_to_manage_name,
    openstack_networking_secgroup_v2.attacker.name
  ]

  network {
    name = "attacker_network"
  }

  depends_on = [openstack_networking_subnet_v2.attacker_subnet]
}
