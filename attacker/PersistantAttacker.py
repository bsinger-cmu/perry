import requests

from .Attacker import Attacker


class PersistantAttacker(Attacker):
    def start_operation(self):
        json_data = {
            "name": "Persistant Operation",
            "id": self.operation_id,
            "adversary": {
                "adversary_id": "deception_enterprise",
            },
            "planner": {
                "id": "persistant_planner",
            },
            "source": {
                "id": "ed32b9c3-9593-4c33-b0db-e2007315096b",
            },
        }

        response = requests.post(
            "http://localhost:8888/api/v2/operations",
            headers=self.api_headers,
            json=json_data,
        )
