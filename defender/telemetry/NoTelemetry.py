from .TelemetryAnalysis import TelemetryAnalysis

from .events import HighLevelEvent


class NoTelemetry(TelemetryAnalysis):
    def process_low_level_events(self) -> list[HighLevelEvent]:
        return []
