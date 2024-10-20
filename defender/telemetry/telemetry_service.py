from typing import Dict, List, Callable, Type, TypeVar
from defender.telemetry.events.event import Event
from .TelemetryAnalysis import TelemetryAnalysis


# Type variable for the event type, must be a subclass of Event
E = TypeVar("E", bound=Event)


# Telemetry Service class that handles subscriptions and publishing events
class TelemetryService:
    def __init__(self, telemetry_analysis: TelemetryAnalysis):
        # We store subscribers as a dictionary where the key is the event type,
        # and the value is a list of handler functions for that event type.
        self.subscribers: Dict[Type[Event], List[Callable[[Event], None]]] = {}
        self.telemetry_analysis = telemetry_analysis

    def process_telemetry(self):
        new_telemetry = self.telemetry_analysis.get_new_telemetry()
        high_level_events = self.telemetry_analysis.process_low_level_events(
            new_telemetry
        )
        for event in high_level_events:
            self.emit(event)

    def subscribe(self, event_type: Type[E], handler: Callable[[E], None]):
        """Subscribe a handler to a specific event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        # Append the handler to the correct event type
        # Even though the base class is Event, Python allows us to subscribe to subclasses
        self.subscribers[event_type].append(handler)  # type: ignore

    def emit(self, event: Event):
        """Emit an event to all subscribers that are subscribed to the event's type."""
        event_type = type(event)
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(event)
