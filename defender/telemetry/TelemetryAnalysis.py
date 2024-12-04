from .events import Event
from elasticsearch import Elasticsearch
from environment.network import Network

from abc import ABC, abstractmethod

from utility.logging import PerryLogger

logger = PerryLogger.get_logger()


class TelemetryAnalysis(ABC):
    def __init__(self, elasticsearch_conn: Elasticsearch, network: Network):
        self.elasticsearch_conn = elasticsearch_conn
        self.network = network
        self.parsed_telemetry_ids = set()

        if not self.elasticsearch_conn.indices.exists(index="sysflow"):
            self.elasticsearch_conn.indices.create(index="sysflow")

    def get_new_telemetry(self) -> list[dict]:
        # Query last 10s of sysflow data with category network
        ssh_process = {
            "bool": {
                "must": [
                    {"range": {"@timestamp": {"gte": "now-10s"}}},
                    {
                        "bool": {
                            "should": [
                                {"match": {"event.category": "process"}},
                                {"match": {"process.name": "ssh"}},
                            ]
                        }
                    },
                ]
            }
        }

        network_traces = {
            "bool": {
                "must": [
                    {"range": {"@timestamp": {"gte": "now-10s"}}},
                    {
                        "bool": {
                            "should": [
                                {"match": {"event.category": "network"}},
                            ]
                        }
                    },
                ]
            }
        }

        process_data = self.elasticsearch_conn.search(
            index="sysflow", query=ssh_process
        )
        traces_data = self.elasticsearch_conn.search(
            index="sysflow", query=network_traces
        )

        # Get documents from query
        raw_telemetry = process_data["hits"]["hits"] + traces_data["hits"]["hits"]

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
