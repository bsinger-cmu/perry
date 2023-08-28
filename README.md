# Setup platform

## Setup python environment

1. Install conda (if not already installed)

2. Create environment: `conda env create -f conda_environment.yml`

3. Activate environment: `conda activate openstack`

## Start an elasticsearch database

We already have an elasticsearch database running, please skip this section
and ask for the credentials :)

1. Run `docker pull docker.elastic.co/elasticsearch/elasticsearch:8.6.2`

2. Create elastic docker network `docker network create elastic`

3. Start the database `docker run --name elasticsearch --net elastic -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -t docker.elastic.co/elasticsearch/elasticsearch:8.6.2`

For a visual interface you can start Kibana:

1. Pull image `docker pull docker.elastic.co/kibana/kibana:8.6.2`

2. Start image `docker run --name kibana --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.6`

**Note**: If you already created the containers (or if they are somehow down), you can start them with `docker start elasticsearch` and `docker start kibana`

## Start a Caldera server

In a new terminal window:

1. Clone the following repo (Brian's fork of Caldera) WITH the `--recursive` flag: https://github.com/bsinger98/caldera
    - `git clone https://github.com/bsinger98/caldera.git --recursive`

2. Add our plugin to Caldera:
    - `cd caldera/plugins`
    - `mkdir deception`
    - `git clone git@github.com:DeceptionProjects/DeceptionCalderaPlugin.git deception/`

3. Create another Conda environment for caldera:
    - `cd ..`
    - `conda create --name caldera`
    - `conda activate caldera`

4. Install caldera required packages
    - `pip3 install -r requirements.txt`

5. Run caldera: `python3 server.py --insecure --fresh`
    - Default ports can be changed by modifying the config file at `conf/default.yml`
    - Check if caldera is running by going to: localhost:8888
    - The credentials for logging in can be found in the configuration file: https://github.com/bsinger98/caldera/blob/master/conf/default.yml

## Running demo code

1. Create a `clouds.yaml` file for your configuration (look at `clouds_example.yaml` for a reference). Take note of username, password, and project name fields.

2. In `deployment_instance/` create a `credentials.tfvars` (an example is in `credentials_example.tfvars`). Note that you will need to replace the openstack username, password, and project name to match other configs.

3. In `config/` create a configuration file (an example is in `config/config_example.yml`). Note that you will need to add the caldera API key and the Elasticsearch user's password.

4. To run, see section "Running the Emulator".

# GUI locations

There are three GUIs that are useful: Openstack, Elasticsearch, and Caldera

- Openstack: 10.20.20.1:443
- Elasticsearch: localhost:5601
- Caldera: localhost:8888

If you are remote, I recommend using SSH tunnels: `ssh gromit.andrew.cmu.edu -L localhost:8000:10.20.20.1:443` (forwards Openstack dashboard to localhost 8000)

Full command with all three tunnels open `ssh <USERNAME>@gromit.andrew.cmu.edu -L localhost:8000:10.20.20.1:443 -L localhost:5601:localhost:5601 -L localhost:8888:localhost:8888`

# Saving Openstack Instances as Images

You can also use the openstack UI and create a snapshot

- `openstack server image create INSTANCE_ID --name IMAGE_NAME`


# Running the Emulator

To run the emulator in interactive mode and gain access to the emulator's command line interface, run `python InteractiveEmulator.py -i`

There are two pairs of emulator commands: 
- `setup` and `run`
- `load` and `execute`

Commands and their arguments can be found by running `help` in the emulator CLI.

Commands:

- `setup -s scenario.yml -c config.yml` is used to manually setup a scenario with a given config
    - Note that CONFIG_FNAME is NOT the path to the file, rather simply the name of the config file. The emulator will look for the config file in the `config/` directory and for the scenario file in the `scenarios/` directory automatically.
- `run -n NUM` is used to run the loaded scenario NUM times
- `load experiment_config.yml` is used to load an experiment configuration (see `config/experiment_config_example.yml` for an example)
- `execute` is used to run the loaded experiment configuration
    - Will continue running all experiments until completed or until stopped with `ctrl-c`. Note that stopping the emulator with `ctrl-c` during the Main Loop *will* save the results of the experiments and will thus need to be deleted.

For an example of how to use the emulator, run the following commands in the emulator CLI:
1. `load experiment_config_example.yml`
2. `execute`

There is also a `view` command that can be useful to view the configuration and loaded setup. For example, after running the `load` command, run `view experiments` to see the loaded experiment configuration.

The emulator also catches exceptions and errors so that the emulator does not crash. If an error occurs, the emulator will print the error and continue running. If the error is fatal, the emulator will print the error and exit.