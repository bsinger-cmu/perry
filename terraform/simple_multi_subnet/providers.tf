terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "1.47.0"
    }
  }
}

provider "openstack" {
  # Configuration options
   auth_url    = "https://128.237.154.129:5000/v3/"
   insecure    = "true"
}

