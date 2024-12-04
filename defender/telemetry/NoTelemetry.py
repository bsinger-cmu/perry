from .TelemetryAnalysis import TelemetryAnalysis

from .events import Event


class NoTelemetry(TelemetryAnalysis):
    def process_low_level_events(self, new_telemetry: list[dict]) -> list[Event]:
        return []
