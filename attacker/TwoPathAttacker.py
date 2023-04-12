import uuid
import requests


class TwoPathAttacker:

    def __init__(self, caldera_api_key):
        self.caldera_api_key = caldera_api_key

        self.api_headers = {
            'key': self.caldera_api_key,
            'Content-Type': 'application/json',
        }
        return
    
    def start_operation(self):
        self.operation_id = str(uuid.uuid4())
        
        json_data = {
            'name': 'Two Path Operation',
            'id': self.operation_id,
            'adversary': {
                'adversary_id': 'deception_two_path',
            },
            'planner': {
                'id': 'deception_random',
            },
            'source': {
                'id': 'ed32b9c3-9593-4c33-b0db-e2007315096b',
            }
        }

        response = requests.post('http://localhost:8888/api/v2/operations', headers=self.api_headers, json=json_data)

    def still_running(self):
        response = requests.get(f'http://localhost:8888/api/v2/operations/{self.operation_id}', headers=self.api_headers)
        operation_details = response.json()

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