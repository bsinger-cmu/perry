from time import sleep
import requests
from utility.logging.logging import PerryLogger
import uuid
import subprocess


class Attacker:

    def __init__(self, caldera_api_key, operation_id=None):
        self.caldera_api_key = caldera_api_key

        if operation_id is not None:
            self.operation_id = operation_id
        else:
            self.operation_id = str(uuid.uuid4())

        self.api_headers = {
            "key": self.caldera_api_key,
            "Content-Type": "application/json",
        }
        return

    def start_server(self, caldera_python_env, caldera_path):
        # Start Caldera
        self.caldera_process = subprocess.Popen(
            [caldera_python_env, "server.py", "--insecure", "--fresh"],
            cwd=caldera_path,
            stdout=PerryLogger.caldera_log_file,
            stderr=subprocess.STDOUT,
        )

    def stop_server(self):
        if self.caldera_process is not None:
            self.caldera_process.terminate()

    def start_operation(self):
        # Clear old agents if they exist
        self.delete_agents()

        # Wait for a trusted agent to appear
        self.wait_for_trusted_agent()

        json_data = {
            "name": "Test Operation",
            "id": self.operation_id,
            "adversary": {
                "adversary_id": "deception_simple_adv",
            },
            "planner": {
                "id": "deception_simple",
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

    def stop_operation(self):
        # Send patch request
        json_data = {"state": "stop"}
        response = requests.patch(
            f"http://localhost:8888/api/v2/operations/{self.operation_id}",
            headers=self.api_headers,
            json=json_data,
        )

    def get_operation_details(self):
        response = requests.get(
            f"http://localhost:8888/api/v2/operations/{self.operation_id}",
            headers=self.api_headers,
        )
        operation_details = response.json()

        return operation_details

    def still_running(self):
        operation_details = self.get_operation_details()
        if operation_details["state"] == "running":
            return True

        return False

    def get_facts(self):
        response = requests.get(
            f"http://localhost:8888/api/v2/facts/{self.operation_id}",
            headers=self.api_headers,
        )
        raw_json = response.json()

        return raw_json["found"]

    def get_relationships(self):
        response = requests.get(
            f"http://localhost:8888/api/v2/relationships/{self.operation_id}",
            headers=self.api_headers,
        )
        raw_json = response.json()

        return raw_json["found"]

    def get_agents(self):
        response = requests.get(
            f"http://localhost:8888/api/v2/agents", headers=self.api_headers
        )
        response_json = response.json()
        return response_json

    def delete_agents(self):
        agents = self.get_agents()
        for agent in agents:
            resp = requests.delete(
                f'http://localhost:8888/api/v2/agents/{agent["paw"]}',
                headers=self.api_headers,
            )
        return

    def wait_for_trusted_agent(self, timeout=5):
        for i in range(timeout):
            # Wait for agent to check in
            agents = self.get_agents()
            for agent in agents:
                if agent["trusted"] is True:
                    return agent["paw"]

            sleep(1)

        raise Exception("Timeout waiting for agent to check in")

    def cleanup(self):
        self.delete_agents()

        self.stop_server()
        return
