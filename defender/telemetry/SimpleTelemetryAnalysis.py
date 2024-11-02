from .TelemetryAnalysis import TelemetryAnalysis

from .events import Event, DecoyHostInteraction, SSHEvent

from utility.logging import log_event


class SimpleTelemetryAnalysis(TelemetryAnalysis):
    def process_low_level_events(self, new_telemetry: list[dict]) -> list[Event]:
        high_level_events = []

        for alert in new_telemetry:
            alert_data = alert["_source"]

            if alert["_index"] == "sysflow":
                if alert_data["event"]["category"] != "network":
                    continue

                if "destination" in alert_data:
                    if self.network.is_ip_decoy(alert_data["destination"]["ip"]):
                        log_event("Decoy host interaction", alert_data["source"]["ip"])
                        attacker_on_host_event = DecoyHostInteraction(
                            alert_data["source"]["ip"],
                            alert_data["destination"]["ip"],
                        )
                        high_level_events.append(attacker_on_host_event)

        return high_level_events
