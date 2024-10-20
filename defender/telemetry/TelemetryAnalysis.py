from .events import Event
from elasticsearch import Elasticsearch
from deployment_instance.network import Network

from abc import ABC, abstractmethod


class TelemetryAnalysis(ABC):
    def __init__(self, elasticsearch_conn: Elasticsearch, network: Network):
        self.elasticsearch_conn = elasticsearch_conn
        self.network = network
        self.parsed_telemetry_ids = set()

        # Create indeces if they don't exist
        if not self.elasticsearch_conn.indices.exists(index="deception_alerts"):
            self.elasticsearch_conn.indices.create(index="deception_alerts")

        if not self.elasticsearch_conn.indices.exists(index="sysflow"):
            self.elasticsearch_conn.indices.create(index="sysflow")

    def get_new_telemetry(self) -> list[dict]:
        # Get new deception alerts
        last_second_query = {"range": {"@timestamp": {"gte": "now-10s"}}}
        alert_query_data = self.elasticsearch_conn.search(
            index="deception_alerts", query=last_second_query
        )

        # Query last 10s of sysflow data with category network
        last_second_query = {
            "bool": {
                "must": [
                    {"range": {"@timestamp": {"gte": "now-10s"}}},
                ]
            }
        }
        sysflow_data = self.elasticsearch_conn.search(
            index="sysflow", query=last_second_query
        )

        # Get documents from query
        raw_telemetry = alert_query_data["hits"]["hits"]
        raw_telemetry += sysflow_data["hits"]["hits"]

        # Filter out already parsed telemetry
        new_telemetry = [
            alert
            for alert in raw_telemetry
            if alert["_id"] not in self.parsed_telemetry_ids
        ]

        # Add document ids to set of parsed telemetry
        new_document_ids = [alert["_id"] for alert in new_telemetry]
        self.parsed_telemetry_ids.update(new_document_ids)

        return new_telemetry

    @abstractmethod
    def process_low_level_events(self, new_telemetry: list[dict]) -> list[Event]:
        pass
