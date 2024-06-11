import requests

from .Attacker import Attacker
from utility.logging.logging import PerryLogger

logger = PerryLogger.get_logger()


class EquifaxBaselineAttacker(Attacker):
    def start_operation(self):
        logger.debug("Starting Caldera operation...")

        json_data = {
            "name": "Equifax Baseline Operation",
            "id": self.operation_id,
            "adversary": {
                "adversary_id": "deception_enterprise",
            },
            "planner": {
                "id": "equifax_baseline",
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
