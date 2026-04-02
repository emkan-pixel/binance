from __future__ import annotations

import customtkinter as ctk

from p2p_assistant.core.enums import LogLevel, Mode
from p2p_assistant.core.logging_service import LoggingService


class MainWindow(ctk.CTk):
    def __init__(self, logger: LoggingService) -> None:
        super().__init__()
        self.logger = logger
        self.mode = Mode.IDLE

        self.title("P2P Workflow Assistant")
        self.geometry("1200x780")

        self._build()
        self.logger.subscribe(self._append_log)

    def _build(self) -> None:
        self.status_label = ctk.CTkLabel(self, text="Browser Status: Not Started | Session: Unknown | Mode: IDLE | Platform: BINANCE")
        self.status_label.pack(padx=12, pady=8, anchor="w")

        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", padx=12, pady=8)

        buttons = [
            "Open Account", "Account Opened", "Ads Published",
            "Start Review", "Start Live Assistant", "Pause", "Resume", "Stop",
            "Export Detailed Orders", "Export Account Summary", "Open Export Folder",
            "Save Settings", "Reload Accounts",
        ]
        for idx, text in enumerate(buttons):
            btn = ctk.CTkButton(controls, text=text, width=160)
            btn.grid(row=idx // 4, column=idx % 4, padx=6, pady=6, sticky="ew")

        self.log_box = ctk.CTkTextbox(self, width=1150, height=460)
        self.log_box.pack(fill="both", expand=True, padx=12, pady=8)

    def _append_log(self, event) -> None:
        prefix = {
            LogLevel.INFO: "[INFO]",
            LogLevel.WARNING: "[WARNING]",
            LogLevel.ERROR: "[ERROR]",
            LogLevel.SUCCESS: "[SUCCESS]",
        }.get(event.level, "[INFO]")
        line = f"{event.ts.isoformat()} {prefix} {event.message}\n"
        self.log_box.insert("end", line)
        self.log_box.see("end")
