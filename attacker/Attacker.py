import uuid
import requests


class Attacker:

    def __init__(self, caldera_api_key):
        self.caldera_api_key = caldera_api_key

        self.api_headers = {
            'key': self.caldera_api_key,
            'Content-Type': 'application/json',
        }
        return
    
    def start_operation(self):
        # Clear old agents if they exist
        self.delete_agents()

        self.operation_id = str(uuid.uuid4())
        
        json_data = {
            'name': 'Test Operation',
            'id': self.operation_id,
            'adversary': {
                'adversary_id': 'deception_simple_adv',
            },
            'planner': {
                'id': 'deception_simple',
            },
            'source': {
                'id': 'ed32b9c3-9593-4c33-b0db-e2007315096b',
            }
        }

        response = requests.post('http://localhost:8888/api/v2/operations', headers=self.api_headers, json=json_data)
    
    def get_operation_details(self):
        response = requests.get(f'http://localhost:8888/api/v2/operations/{self.operation_id}', headers=self.api_headers)
        operation_details = response.json()

        return operation_details
    
    def still_running(self):
        operation_details = self.get_operation_details()
        if operation_details['state'] == 'running':
            return True
        
        return False
    
    def get_facts(self):
        response = requests.get(f'http://localhost:8888/api/v2/facts/{self.operation_id}', headers=self.api_headers)
        raw_json = response.json()

        return raw_json['found']
    
    def get_relationships(self):
        response = requests.get(f'http://localhost:8888/api/v2/relationships/{self.operation_id}', headers=self.api_headers)
        raw_json = response.json()

        return raw_json['found']
    
    def delete_agents(self):
        response = requests.get(f'http://localhost:8888/api/v2/agents', headers=self.api_headers)
        response_json = response.json()
        for agent in response_json:
            requests.delete(f'http://localhost:8888/api/v2/agents/{agent["paw"]}', headers=self.api_headers)
        return
    
    def cleanup(self):
        self.delete_agents()
        return