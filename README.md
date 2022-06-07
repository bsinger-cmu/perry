# Terraform

## Setup simple network

Setup environment variables: `source ./PROJECT_RC.sh`

Go into terraform directory: `cd terraform/simple_network`

If first time, init terraform: `terraform init`

Then check it is working through: `terraform plan`

Now deploy the network: `terraform apply`

Ping the machine: `ping EXTERNAL_IP_ADDR` or ssh `ssh cirros@EXTERNAL_IP_ADDR`

To destroy: `terraform destroy`