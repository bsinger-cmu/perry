from .TelemetryAnalysis import TelemetryAnalysis

from .events import Event, DecoyHostInteraction, DecoyCredentialUsed

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
                    cmd_ln = alert_data["process"]["command_line"]
                    dest_port = alert_data["destination"]["port"]
                    dest_ip = alert_data["destination"]["ip"]

                    if "destination" in alert_data and "process" in alert_data:
                        # Net cat shell rule
                        if self.network.is_ip_decoy(dest_ip):
                            if (
                                dest_port == 4444
                                and "/usr/bin/ncat --no-shutdown -i" in cmd_ln
                            ):
                                attacker_on_host_event = DecoyHostInteraction(
                                    alert_data["source"]["ip"],
                                    alert_data["destination"]["ip"],
                                )
                                high_level_events.append(attacker_on_host_event)

                        if self.network.is_ip_decoy(alert_data["host"]["ip"]):
                            if dest_port == 8888 and "/usr/bin/curl" in cmd_ln:
                                attacker_on_host_event = DecoyHostInteraction(
                                    alert_data["source"]["ip"],
                                    alert_data["destination"]["ip"],
                                )
                                high_level_events.append(attacker_on_host_event)

        return high_level_events
