from .events import HighLevelEvent


class TelemetryAnalysis:
    def __init__(self, elasticsearch_conn):
        self.elasticsearch_conn = elasticsearch_conn
        self.parsed_telemetry_ids = set()

    def get_new_telemetry(self):
        # Get new deception alerts
        last_second_query = {"query": {"range": {"timestamp": {"gte": "now-5s"}}}}
        alert_query_data = self.elasticsearch_conn.search(
            index="deception_alerts", body=last_second_query
        )

        # Get documents from query
        raw_telemetry = alert_query_data["hits"]["hits"]

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
