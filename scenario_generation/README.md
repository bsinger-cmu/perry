# Terraform

## Setup simple network

Setup environment variables: `source ./PROJECT_RC.sh`

Go into terraform directory: `cd terraform/simple_network`

If first time, init terraform: `terraform init`

Then check it is working through: `terraform plan`

Now deploy the network: `terraform apply`

Ping the machine (Find external IP address from floating IPs in dashboard): `ping EXTERNAL_IP_ADDR` or ssh `ssh -i KEY_PATH cirros@EXTERNAL_IP_ADDR`

To destroy: `terraform destroy`

## Setup cage network

Setup environment variables: `source ./PROJECT_RC.sh`

Go into terraform directory: `cd terraform/cage`

If first time, init terraform: `terraform init`

Then check it is working through: `terraform plan`

Now deploy the network: `terraform apply`

Ping the machine (Find external IP address from floating IPs in dashboard): `ping EXTERNAL_IP_ADDR` or ssh `ssh -i KEY_PATH ubuntu@EXTERNAL_IP_ADDR`

To destroy: `terraform destroy`