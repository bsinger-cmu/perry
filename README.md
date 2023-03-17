
# Setting up cloud environment

We use terraform to create a cloud environment in openstack. `./terraform` contains a README.md detailing how to use.

# Setup platform

## Setup python environment

1. Install conda (if not already installed)

2. `cd interaction_engine`

3. Create environment: `conda env create -f conda_environment.yml`

4. Activate environment: `conda activate openstack`'

## Start an elasticsearch database

1. Run `docker pull docker.elastic.co/elasticsearch/elasticsearch:8.6.2`

2. Create elastic docker network `docker network create elastic`

3. Start the database `docker run --name elasticsearch --net elastic -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -t docker.elastic.co/elasticsearch/elasticsearch:8.6.2`

Note: If you alread created the container, you can start it with `docker start elasticsearch`

For a visual interface you can start Kibana:

1. Pull image `docker pull docker.elastic.co/kibana/kibana:8.6.2`

2. Start image `docker run --name kibana --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.6`

## Start a Caldera server

## Running demo code

1. Create a `clouds.yaml` file for your configuration (look at `clouds_example.yaml` for a reference)

2. In `deployment_instance` create a `credentials.tfvars` (an example is in `credentials_example.tfvars`)

3. In `config` create a configuration file (an example is in `config/config_example.yml`)

4. Run `python3 main.py -c CONFIG_FNAME`
