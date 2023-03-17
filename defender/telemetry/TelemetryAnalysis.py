from .events import HighLevelEvent


class TelemetryAnalysis():

    def __init__(self, elasticsearch_conn):
        self.elasticsearch_conn = elasticsearch_conn
    
    def process_low_level_events() -> HighLevelEvent:
        return HighLevelEvent()