from .events import HighLevelEvent
from elasticsearch import Elasticsearch


class TelemetryAnalysis:
    def __init__(self, elasticsearch_conn: Elasticsearch):
        self.elasticsearch_conn = elasticsearch_conn
        self.parsed_telemetry_ids = set()

        # Create indeces if they don't exist
        if not self.elasticsearch_conn.indices.exists(index="deception_alerts"):
            self.elasticsearch_conn.indices.create(index="deception_alerts")

        if not self.elasticsearch_conn.indices.exists(index="sysflow"):
            self.elasticsearch_conn.indices.create(index="sysflow")

    def get_new_telemetry(self):
        # Get new deception alerts
        last_second_query = {"range": {"@timestamp": {"gte": "now-10s"}}}
        alert_query_data = self.elasticsearch_conn.search(
            index="deception_alerts", query=last_second_query
        )

        last_second_query = {
            "bool": {
                "must": [
                    {"range": {"@timestamp": {"gte": "now-10s"}}},
                    {"term": {"category": "network"}},
                    {"term": {"destination.ip": "192.168.200.3"}},
                    {"term": {"destination.port": "22"}},
                    {"term": {"source.ip": "192.168.200.4"}},
                ]
            },
        }

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

    def process_low_level_events(self) -> list[HighLevelEvent]:
        return []
