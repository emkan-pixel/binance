from __future__ import annotations

from pathlib import Path

from p2p_assistant.core.logging_service import LoggingService
from p2p_assistant.persistence.db import init_db
from p2p_assistant.ui.main_window import MainWindow


def main() -> None:
    base = Path.home() / ".p2p_assistant"
    init_db(base / "app.db")
    logger = LoggingService()
    app = MainWindow(logger)
    from p2p_assistant.core.enums import LogLevel
    logger.emit(LogLevel.INFO, "Application initialized.")
    app.mainloop()


if __name__ == "__main__":
    main()
