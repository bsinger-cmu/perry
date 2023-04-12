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

    def get_operation_status(self):
        response = requests.get(f'http://localhost:8888/api/v2/operations/{self.operation_id}', headers=self.api_headers)
        response_json = response.json()
        print(response_json['state'])
        return