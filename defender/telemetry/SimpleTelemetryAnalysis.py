from .TelemetryAnalysis import TelemetryAnalysis

from .events import HighLevelEvent, AttackerOnHost, SSHEvent

from utility.logging import log_event


class SimpleTelemetryAnalysis(TelemetryAnalysis):
    def process_low_level_events(self) -> list[HighLevelEvent]:
        high_level_events = []
        new_telemetry = self.get_new_telemetry()

        for alert in new_telemetry:
            alert_data = alert["_source"]

            if alert["_index"] == "sysflow":
                if alert_data["event"]["category"] != "network":
                    continue
                # if destination in alert data
                if "destination" in alert_data:
                    if alert_data["destination"]["port"] == 22:
                        ssh_event = SSHEvent(
                            alert_data["source"]["ip"],
                            alert_data["destination"]["ip"],
                            alert_data["destination"]["port"],
                        )
                        high_level_events.append(ssh_event)

        return high_level_events
