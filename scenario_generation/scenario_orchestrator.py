import subprocess
import os

def deploy_network(name):
    deployment_dir = os.path.join('scenario_generation', name)

    print('Deploying network (might take a minute)...')
    process = subprocess.Popen(['terraform', 'apply', '-var-file=../credentials.tfvars', '-auto-approve'], 
                                cwd=deployment_dir,
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
    
    stdout, stderr = process.communicate()
    print('Finished!')

def destroy_network(name):
    deployment_dir = os.path.join('scenario_generation', name)

    print('Destroying network...')
    process = subprocess.Popen(['terraform', 'destroy', '-var-file=../credentials.tfvars', '-auto-approve'], 
                                cwd=deployment_dir,
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
    
    stdout, stderr = process.communicate()
    print('Finished!')