######### Setup Networking #########
# External network is not managed by terraform, need to set as datasource
data "openstack_networking_network_v2" "external_network" {
  name = "external"
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

resource "openstack_networking_network_v2" "company_network" {
  name           = "company_network"
  admin_state_up = "true"
  description    = "Internal company network"
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

resource "openstack_networking_subnet_v2" "company_subnet" {
  name            = "company_network"
  network_id      = openstack_networking_network_v2.company_network.id
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

######### Setup Compute #########

### Management Host ###
resource "openstack_compute_instance_v2" "manage_host" {
  name        = "manage_host"
  image_name  = "ubuntu20_pip"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name

  network {
    name = "manage_network"
  }
}

resource "openstack_compute_floatingip_associate_v2" "fip_manage" {
  floating_ip = openstack_networking_floatingip_v2.manage_floating_ip.address
  instance_id = openstack_compute_instance_v2.manage_host.id
}

resource "openstack_networking_floatingip_v2" "manage_floating_ip" {
  pool = "external"
}

### Webserver Subnet Hosts ###
resource "openstack_compute_instance_v2" "webserver_A" {
  name        = "webserver_A"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.webserver.name
  ]

  network {
    name        = "webserver_network"
    fixed_ip_v4 = "192.168.200.4"
  }
}

resource "openstack_compute_instance_v2" "webserver_B" {
  name        = "webserver_B"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.webserver.name
  ]

  network {
    name        = "webserver_network"
    fixed_ip_v4 = "192.168.200.5"
  }
}

resource "openstack_compute_instance_v2" "webserver_C" {
  name        = "webserver_C"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.webserver.name
  ]

  network {
    name        = "webserver_network"
    fixed_ip_v4 = "192.168.200.6"
  }
}

### Corporate Network Hosts ###
resource "openstack_compute_instance_v2" "user_A" {
  name        = "user_A"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "company_network"
    fixed_ip_v4 = "192.168.202.4"
  }
}

resource "openstack_compute_instance_v2" "user_B" {
  name        = "user_B"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "company_network"
    fixed_ip_v4 = "192.168.202.5"
  }
}

resource "openstack_compute_instance_v2" "user_C" {
  name        = "user_C"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "company_network"
    fixed_ip_v4 = "192.168.202.6"
  }
}

resource "openstack_compute_instance_v2" "user_D" {
  name        = "user_D"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "company_network"
    fixed_ip_v4 = "192.168.202.7"
  }
}

### Critical Datacenter Hosts ###
resource "openstack_compute_instance_v2" "database_A" {
  name        = "database_A"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "critical_company_network"
    fixed_ip_v4 = "192.168.201.4"
  }
}

resource "openstack_compute_instance_v2" "database_B" {
  name        = "database_B"
  image_name  = "ubuntu20_sysflow"
  flavor_name = "m1.small"
  key_pair    = var.perry_key_name
  security_groups = [
    openstack_networking_secgroup_v2.talk_to_manage.name,
    openstack_networking_secgroup_v2.critical_company.name
  ]

  network {
    name        = "critical_company_network"
    fixed_ip_v4 = "192.168.201.5"
  }
}
