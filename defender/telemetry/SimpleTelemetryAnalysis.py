from .TelemetryAnalysis import TelemetryAnalysis

from .events import HighLevelEvent, AttackerOnHost


class SimpleTelemetryAnalysis(TelemetryAnalysis):

    def __init__(self, elasticsearch_conn):
        super().__init__(elasticsearch_conn)

        self.parsed_telemetry_ids = set()

    def get_new_telemetry(self):
        # Get new deception alerts
        last_second_query = {"query": {"range": {"timestamp": {"gte": "now-1s"}}}}
        alert_query_data = self.elasticsearch_conn.search(index='deception_alerts', body=last_second_query)

        # Get documents from query
        raw_telemetry = alert_query_data['hits']['hits']

        # Filter out already parsed telemetry
        new_telemetry = [alert for alert in raw_telemetry if alert['_id'] not in self.parsed_telemetry_ids]

        # Add document ids to set of parsed telemetry
        new_document_ids = [alert['_id'] for alert in new_telemetry]
        self.parsed_telemetry_ids.update(new_document_ids)

        return new_telemetry

    def process_low_level_events(self):
        high_level_events = []

        new_telemetry = self.get_new_telemetry()

        for alert in new_telemetry:
            alert_data = alert['_source']
            # If honey service interaction create attacker on host event 
            if alert_data['type'] == 'honey_service':
                attacker_host = alert_data['from_host']
                high_level_events.append(AttackerOnHost(attacker_host))
        
        return high_level_events