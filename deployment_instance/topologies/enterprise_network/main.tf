######### Setup Networking #########
# External network is not managed by terraform, need to set as datasource
data "openstack_networking_network_v2" "external_network" {
  name = "external"
}

resource "openstack_networking_network_v2" "manage_network" {
  name           = "manage_network"
  admin_state_up = "true"
}

resource "openstack_networking_network_v2" "company_network" {
  name           = "company_network"
  admin_state_up = "true"
  description    = "company's office building network"
}

resource "openstack_networking_network_v2" "datacenter_network" {
  name           = "datacenter_network"
  admin_state_up = "true"
  description    = "hosts the company's internal database"
}

### Subnets ###
resource "openstack_networking_subnet_v2" "manage" {
  name       = "manage"
  network_id = "${openstack_networking_network_v2.manage_network.id}"
  cidr       = "192.168.198.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "company_subnet" {
  name       = "company_subnet"
  network_id = "${openstack_networking_network_v2.company_network.id}"
  cidr       = "192.168.200.0/24"
  ip_version = 4
}

resource "openstack_networking_subnet_v2" "datacenter_subnet" {
  name       = "datacenter_subnet"
  network_id = "${openstack_networking_network_v2.datacenter_network.id}"
  cidr       = "192.168.201.0/24"
  ip_version = 4
}

### Ports ###
# Host Ports
resource "openstack_networking_port_v2" "manage_port_host" {
  name               = "manage_port_host"
  network_id         = "${openstack_networking_network_v2.manage_network.id}"
  admin_state_up     = "true"
  security_group_ids = ["${openstack_networking_secgroup_v2.manage_freedom.id}"]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.manage.id}"
  }
}

resource "openstack_networking_port_v2" "activedir_company_port" {
  name               = "activedir_company_port"
  network_id         = "${openstack_networking_network_v2.company_network.id}"
  admin_state_up     = "true"
  security_group_ids = [
    "${openstack_networking_secgroup_v2.talk_to_manage.id}",
    "${openstack_networking_secgroup_v2.company.id}"
  ]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.company_subnet.id}"
    ip_address = "192.168.200.3"
  }
}

resource "openstack_networking_port_v2" "ceo_company_port" {
  name               = "ceo_company_port"
  network_id         = "${openstack_networking_network_v2.company_network.id}"
  admin_state_up     = "true"
  security_group_ids = [
    "${openstack_networking_secgroup_v2.talk_to_manage.id}",
    "${openstack_networking_secgroup_v2.company.id}"
  ]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.company_subnet.id}"
    ip_address = "192.168.200.4"
  }
}

resource "openstack_networking_port_v2" "finance_company_port" {
  name               = "finance_company_port"
  network_id         = "${openstack_networking_network_v2.company_network.id}"
  admin_state_up     = "true"
  security_group_ids = [
    "${openstack_networking_secgroup_v2.talk_to_manage.id}",
    "${openstack_networking_secgroup_v2.company.id}"
  ]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.company_subnet.id}"
    ip_address = "192.168.200.5"
  }
}

resource "openstack_networking_port_v2" "hr_company_port" {
  name               = "hr_company_port"
  network_id         = "${openstack_networking_network_v2.company_network.id}"
  admin_state_up     = "true"
  security_group_ids = [
    "${openstack_networking_secgroup_v2.talk_to_manage.id}",
    "${openstack_networking_secgroup_v2.company.id}"
  ]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.company_subnet.id}"
    ip_address = "192.168.200.6"
  }
}

resource "openstack_networking_port_v2" "intern_company_port" {
  name               = "intern_company_port"
  network_id         = "${openstack_networking_network_v2.company_network.id}"
  admin_state_up     = "true"
  security_group_ids = [
    "${openstack_networking_secgroup_v2.talk_to_manage.id}", 
    "${openstack_networking_secgroup_v2.company.id}"
  ]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.company_subnet.id}"
    ip_address = "192.168.200.7"
  }
}

resource "openstack_networking_port_v2" "database_datacenter_port" {
  name               = "database_datacenter_port"
  network_id         = "${openstack_networking_network_v2.datacenter_network.id}"
  admin_state_up     = "true"
  security_group_ids = [
    "${openstack_networking_secgroup_v2.talk_to_manage.id}", 
    "${openstack_networking_secgroup_v2.datacenter.id}"
  ]

  fixed_ip {
    subnet_id  = "${openstack_networking_subnet_v2.datacenter_subnet.id}"
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
resource "openstack_networking_router_interface_v2" "router_interface_manage_company" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.company_subnet.id}"
}

resource "openstack_networking_router_interface_v2" "router_interface_manage_datacenter" {
  router_id = "${openstack_networking_router_v2.router_external.id}"
  subnet_id = "${openstack_networking_subnet_v2.datacenter_subnet.id}"
}

######### Setup Compute #########

### Management Host ###
resource "openstack_compute_instance_v2" "manage_host" {
  name            = "manage_host"
  image_name      = "ubuntu20_pip"
  flavor_name     = "m1.small"
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

### Company Subnet Hosts ###
resource "openstack_compute_instance_v2" "activedir_host" {
  name            = "activedir_host"
  image_name      = "ubuntu20_sysflow"
  flavor_name     = "m1.small"
  key_pair        = "cage"
  
  network {
    port = "${openstack_networking_port_v2.activedir_company_port.id}"
  }
}

resource "openstack_compute_instance_v2" "ceo_host" {
  name            = "ceo_host"
  image_name      = "ubuntu20_sysflow"
  flavor_name     = "m1.small"
  key_pair        = "cage"
  
  network {
    port = "${openstack_networking_port_v2.ceo_company_port.id}"
  }
}

resource "openstack_compute_instance_v2" "finance_host" {
  name            = "finance_host"
  image_name      = "ubuntu20_sysflow"
  flavor_name     = "m1.small"
  key_pair        = "cage"

  network {
    port = "${openstack_networking_port_v2.finance_company_port.id}"
  }
}

resource "openstack_compute_instance_v2" "hr_host" {
  name            = "hr_host"
  image_name      = "ubuntu20_sysflow"
  flavor_name     = "m1.small"
  key_pair        = "cage"

  network {
    port = "${openstack_networking_port_v2.hr_company_port.id}"
  }
}

resource "openstack_compute_instance_v2" "intern_host" {
  name            = "intern_host"
  image_name      = "ubuntu20_sysflow"
  flavor_name     = "m1.small"
  key_pair        = "cage"

  network {
    port = "${openstack_networking_port_v2.intern_company_port.id}"
  }
}

### Datacenter Subnet Hosts ###
resource "openstack_compute_instance_v2" "database_host" {
  name            = "database_host"
  image_name      = "ubuntu20_sysflow"
  flavor_name     = "m1.small"
  key_pair        = "cage"
  
  network {
    port = "${openstack_networking_port_v2.database_datacenter_port.id}"
  }
}