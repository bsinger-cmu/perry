# Setting up python environment

1. Install conda (if not already installed)

2. Create environment: `conda env create -f environment.yml`

3. Activate environment: `conda activate openstack`

# Running openstack

1. Create a `clouds.yaml` file for your configuration (look at `clouds_example.yaml` for a reference)

2. Run `python openstackAPI.py`

# Running ansible runner

`python ansibleRunner.py -ssh_key_path=~/snap/microstack/common/.ssh/id_microstack`

# Adding a package

1. Add package, export to yml: `conda env export > conda_environment.yml`

