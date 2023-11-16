from .TelemetryAnalysis import TelemetryAnalysis

from .events import HighLevelEvent, AttackerOnHost

from utility.logging import log_event


class SimpleTelemetryAnalysis(TelemetryAnalysis):
    def process_low_level_events(self) -> list[HighLevelEvent]:
        high_level_events = []
        new_telemetry = self.get_new_telemetry()

        for alert in new_telemetry:
            log_event("New telemetry low-level alert", alert["_id"])
            alert_data = alert["_source"]
            # If honey service interaction create attacker on host event
            if alert_data["type"] == "honey_service":
                attacker_host = alert_data["from_host"]
                high_level_events.append(AttackerOnHost(attacker_host))

        return high_level_events
