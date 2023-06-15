# Setup platform

## Setup python environment

1. Install conda (if not already installed)

2. Create environment: `conda env create -f conda_environment.yml`

3. Activate environment: `conda activate openstack`'

## Start an elasticsearch database

We already have an elasticsearch database running, please skip this step
and ask for the credentials :)

1. Run `docker pull docker.elastic.co/elasticsearch/elasticsearch:8.6.2`

2. Create elastic docker network `docker network create elastic`

3. Start the database `docker run --name elasticsearch --net elastic -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -t docker.elastic.co/elasticsearch/elasticsearch:8.6.2`

For a visual interface you can start Kibana:

1. Pull image `docker pull docker.elastic.co/kibana/kibana:8.6.2`

2. Start image `docker run --name kibana --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.6`

Note: If you already created the containers, you can start them with `docker start elasticsearch` and `docker start kibana`

## Start a Caldera server

In a new terminal window:

1. Clone the following repo (Brian's fork of Caldera) WITH the `--recursive` flag: https://github.com/bsinger98/caldera

`git clone https://github.com/bsinger98/caldera.git --recursive`

2. Add our plugin to Caldera:

`cd caldera/plugins`

`git clone git@github.com:DeceptionProjects/DeceptionCalderaPlugin.git`

Rename the repo: `mv DeceptionCalderaPlugin deception`

3. Create another Conda environment for caldera:

`cd ..`

`conda create --name caldera`

`conda activate caldera`

4. Install caldera packages

`pip3 install -r requirements.txt`

5. Run caldera: `python3 server.py --insecure --fresh`

Check if caldera is running by going to: localhost:8888

The credentials for logging in can be found in the configuration file: https://github.com/bsinger98/caldera/blob/master/conf/default.yml

## Running demo code

1. Create a `clouds.yaml` file for your configuration (look at `clouds_example.yaml` for a reference). Take note of username, password, and project name fields.

2. In `deployment_instance/` create a `credentials.tfvars` (an example is in `credentials_example.tfvars`). Note that you will need to replace the openstack username, password, and project name to match other configs.

3. In `config/` create a configuration file (an example is in `config/config_example.yml`). Note that you will need to add the elasticsearch and caldera API keys (different from login keys)

4. To run `python3 main.py -c CONFIG_FNAME` Note that CONFIG_FNAME is NOT the path to the file, rather simply the name of the config file.

An example: `python3 emulator.py -c CONFIG_FNAME`

# GUI locations

There are three GUIs that are useful: Openstack, Elasticsearch, and Caldera

Openstack: 10.20.20.1:443

Elasticsearch: localhost:5601

Caldera: localhost:8888

If you are remote, I recommend using SSH tunnels: `ssh gromit.andrew.cmu.edu -L localhost:8000:10.20.20.1:443` (forwards Openstack dashboard to localhost 8000)

Full command with all three tunnels open `ssh <USERNAME>@gromit.andrew.cmu.edu -L localhost:8000:10.20.20.1:443 -L localhost:5601:localhost:5601 -L localhost:8888:localhost:8888`

or `ssh gromit -L localhost:5601:localhost:5601`

# Saving Openstack Instances as Images

You can also use the openstack UI and create a snapshot

`openstack server image create INSTANCE_ID --name IMAGE_NAME`
