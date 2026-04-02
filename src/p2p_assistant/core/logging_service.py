from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List

from p2p_assistant.core.enums import LogLevel


@dataclass
class LogEvent:
    ts: datetime
    level: LogLevel
    message: str


class LoggingService:
    def __init__(self) -> None:
        self._subscribers: List[Callable[[LogEvent], None]] = []

    def subscribe(self, callback: Callable[[LogEvent], None]) -> None:
        self._subscribers.append(callback)

    def emit(self, level: LogLevel, message: str) -> None:
        event = LogEvent(ts=datetime.utcnow(), level=level, message=message)
        for callback in self._subscribers:
            callback(event)
