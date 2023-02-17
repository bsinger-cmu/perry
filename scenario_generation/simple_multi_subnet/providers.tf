terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "1.47.0"
    }
  }
}

# No default value
variable "project_name" {
   type = string
   description = "Openstack project"
}

# No default value
variable "openstack_username" {
   type = string
   description = "Openstack username"
}

# default value for the variable location
variable "openstack_password" {
   type = string
   description = "Openstack password"
}


# provider "openstack" {
#   # Configuration options
#    auth_url    = "https://128.237.154.129:5000/v3/"
#    insecure    = "true"
# }

# Configure the OpenStack Provider
provider "openstack" {
  user_name   = var.openstack_username
  tenant_name = var.project_name
  password    = var.openstack_password
  auth_url    = "https://128.237.154.129:5000/v3/"
  region      = "microstack"
  insecure    = "true"
}



