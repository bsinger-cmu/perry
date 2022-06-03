resource "openstack_compute_instance_v2" "test" {
  name            = "test-vm"
  image_name      = "cirros"
  flavor_name     = "m1.tiny"
  security_groups = ["default"]

  network {
    name = "simple_network"
  }
}