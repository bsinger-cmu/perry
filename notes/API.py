import os
import requests
import pprint

def get_API_KEY(CALDERA_PATH):
    PATH = os.path.join(CALDERA_PATH, "conf/", "local.yml")
    if (not os.path.isfile(PATH)) or (not os.access(PATH, os.R_OK)):
        print("local.yml file does not exist or is not readable.")
    f = open(PATH)
    lines = f.readlines()
    API_KEY = lines[2].split(": ")[1].strip()
    return API_KEY

def list_operations(API_KEY):
    headers = {
        'key': f"{API_KEY}",
        'Content-Type': 'application/json',
    }
    response = requests.get('http://localhost:8888/api/v2/operations', headers=headers)
    return response

def list_adversaries(API_KEY):
    headers = {
    'key': f"{API_KEY}",
    }
    json_data = {
        'index': 'adversaries',
    }
    response = requests.post('http://localhost:8888/api/rest', headers=headers, json=json_data)
    return response

def create_adversary(API_KEY, description="test", objective="string", atomic_ordering=["string"], tags=['string'], adversary_id="string", name="test"):
    headers = {
    'key': f"{API_KEY}",
    }
    json_data = {
        'description': description,
        'objective': objective,
        'atomic_ordering': atomic_ordering,
        'tags': tags,
        'plugin': None,
        'adversary_id': adversary_id,
        'name': name,
    }
    response = requests.post('http://localhost:8888/api/v2/adversaries', headers=headers, json=json_data)
    return response

def create_operation(API_KEY):
    pass


if __name__ == "__main__":
    CALDERA_PATH = "/home/kali/caldera"

    API_KEY = get_API_KEY(CALDERA_PATH)
    print("API_KEY: {}".format(API_KEY))

    operations = list_operations(API_KEY)
    # pprint.pprint(operations.json())

    adversaries = list_adversaries(API_KEY)
    # pprint.pprint(adversaries.json())
    # print([adv['name'] for adv in adversaries.json()])

    response = create_adversary(API_KEY, name="TEST", adversary_id="TEST1")
    pprint.pprint(response.json())