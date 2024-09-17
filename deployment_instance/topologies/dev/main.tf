# Docker Provider
provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Pulls the image
resource "docker_image" "ubuntu" {
  name = "ubuntu:latest"
}

# Create Docker network for Ubuntu hosts
resource "docker_network" "attacker_network" {
  name = "attacker_network"
  ipam_config {
    subnet = "192.168.202.0/24"
  }
}

resource "docker_network" "webserver_network" {
  name = "webserver_network"
  ipam_config {
    subnet = "192.168.201.0/24"
  }
}


resource "docker_container" "attacker" {
  count    = 1
  image    = docker_image.ubuntu.name
  name     = "attacker"
  networks_advanced {
    name = docker_network.attacker_network.name
  }
  privileged = true
  command = ["/bin/bash", "-c", "while true; do sleep 3600; done"]
}

resource "docker_container" "webserver" {
  count    = 1
  image    = docker_image.ubuntu.name
  name     = "webserver"
  networks_advanced {
    name = docker_network.webserver_network.name
  }
  privileged = true
  command = ["/bin/bash", "-c", "while true; do sleep 3600; done"]
}