import subprocess
import os
import time


def deploy_network(name):
    deployment_dir = os.path.join("environment/topologies", name)

    print("Initializing Terraform directory...")
    result = subprocess.run(
        ["terraform", "init"], cwd=deployment_dir, capture_output=True, text=True
    )

    print("Deploying network (might take a minute)...")
    process = subprocess.Popen(
        ["terraform", "apply", "-var-file=../../credentials.tfvars", "-auto-approve"],
        cwd=deployment_dir,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )

    stdout, stderr = process.communicate()

    # Wait a few seconds for the network to be deployed
    # TODO ping server to see if it is up
    print("Finished!")


def destroy_network(name):
    deployment_dir = os.path.join("environment/topologies", name)

    print("Destroying network (might take a minute)...")
    process = subprocess.Popen(
        ["terraform", "destroy", "-var-file=../../credentials.tfvars", "-auto-approve"],
        cwd=deployment_dir,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )

    stdout, stderr = process.communicate()
    print("Finished!")
