import uuid
import requests

from .Attacker import Attacker


class EnterpriseAttacker(Attacker):

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
            'name': 'Enterprise Operation',
            'id': self.operation_id,
            'adversary': {
                'adversary_id': 'deception_enterprise',
            },
            'planner': {
                'id': 'deception_enterprise',
            },
            'source': {
                'id': 'ed32b9c3-9593-4c33-b0db-e2007315096b',
            }
        }

        response = requests.post('http://localhost:8888/api/v2/operations', headers=self.api_headers, json=json_data)