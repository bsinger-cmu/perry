terraform {
required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "1.47.0"
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  # user_name   = "yinuo"
  # tenant_name = "admin"
  # password    = "dvz0ght9CQY*jpd7eng"
  auth_url    = "https://128.237.154.129:5000/v3/"
  region      = "microstack"
  insecure    = "true"
}

# Create a web server
resource "openstack_compute_instance_v2" "basic" {
  name = "basic"
  flavor_name     = "m1.small"
  security_groups = ["default"]
  network {
    name = "int-net"
  }
}