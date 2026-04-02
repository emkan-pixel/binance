from enum import Enum


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class Mode(str, Enum):
    IDLE = "IDLE"
    REVIEW = "REVIEW"
    LIVE = "LIVE"


class Platform(str, Enum):
    BINANCE = "BINANCE"
    OKX = "OKX"
    BYBIT = "BYBIT"
