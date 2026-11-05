"""Event bus for inter-module communication."""

from collections.abc import Callable
from typing import Any

EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    """Simple in-memory event bus for module communication."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event_type: str, data: dict[str, Any]) -> None:
        """Publish an event."""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(data)


# Global event bus instance
event_bus = EventBus()
