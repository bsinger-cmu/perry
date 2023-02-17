
# Setting up cloud environment

We use terraform to create a cloud environment in openstack. `./terraform` contains a README.md detailing how to use.

# Setup interaction code

## Setup python environment

1. Install conda (if not already installed)

2. `cd interaction_engine`

3. Create environment: `conda env create -f conda_environment.yml`

4. Activate environment: `conda activate openstack`

## Running demo code

1. Create a `clouds.yaml` file for your configuration (look at `clouds_example.yaml` for a reference)

2. In `scenario_generation` create a `credentials.tfvars` (an example is in `credentials_example.tfvars`)

3. Run `python cage_simulation -s SSH_KEY_PATH -a ./ansible/cage`
