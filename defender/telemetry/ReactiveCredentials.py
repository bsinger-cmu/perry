from .TelemetryAnalysis import TelemetryAnalysis

from .events import Event, SSHEvent, DecoyCredentialUsed

from utility.logging import PerryLogger

logger = PerryLogger.get_logger()


class ReactiveCredentials(TelemetryAnalysis):
    def process_low_level_events(self, new_telemetry: list[dict]) -> list[Event]:
        high_level_events = []

        for alert in new_telemetry:
            alert_data = alert["_source"]

            if alert["_index"] == "sysflow":

                # Honey credential alert
                if alert_data["event"]["category"] == "process":
                    if alert_data["process"]["name"] == "ssh":
                        for decoy_user in self.network.get_all_decoy_users():
                            if decoy_user in alert_data["process"]["command_line"]:
                                cred_event = DecoyCredentialUsed(
                                    alert_data["host"]["ip"], decoy_user
                                )
                                high_level_events.append(cred_event)

                if alert_data["event"]["category"] == "network":
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
