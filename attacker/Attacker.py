import requests


class Attacker:

    def __init__(self, caldera_api_key):
        self.caldera_api_key = caldera_api_key
        return
    
    def start_operation(self):
        headers = {
            'key': self.caldera_api_key,
            'Content-Type': 'application/json',
        }

        json_data = {
            'name': 'Test Operation',
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

        response = requests.post('http://localhost:8888/api/v2/operations', headers=headers, json=json_data)