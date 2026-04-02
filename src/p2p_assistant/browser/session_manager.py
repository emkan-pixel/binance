from __future__ import annotations

from pathlib import Path
from typing import Optional

from playwright.sync_api import BrowserContext, Page, sync_playwright

from p2p_assistant.core.enums import LogLevel
from p2p_assistant.core.logging_service import LoggingService


class BrowserSessionManager:
    def __init__(self, user_data_dir: Path, logger: LoggingService, headless: bool = False) -> None:
        self.user_data_dir = user_data_dir
        self.logger = logger
        self.headless = headless
        self._playwright = None
        self._context: Optional[BrowserContext] = None

    def start(self) -> BrowserContext:
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        self._playwright = sync_playwright().start()
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )
        self.logger.emit(LogLevel.SUCCESS, f"Browser started with persistent profile: {self.user_data_dir}")
        return self._context

    def ensure_context(self) -> BrowserContext:
        if self._context is None:
            return self.start()
        return self._context

    def ensure_page(self) -> Page:
        context = self.ensure_context()
        if context.pages:
            page = context.pages[0]
            if page.is_closed():
                self.logger.emit(LogLevel.WARNING, "Primary page was closed; creating a new page.")
                return context.new_page()
            return page
        return context.new_page()

    def safe_goto(self, page: Page, url: str, timeout_ms: int = 60000) -> bool:
        try:
            page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            return True
        except Exception as exc:
            self.logger.emit(LogLevel.ERROR, f"Navigation error: {exc}")
            self.logger.emit(LogLevel.WARNING, "Attempting recovery by recreating page.")
            try:
                new_page = self.ensure_context().new_page()
                new_page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
                return True
            except Exception as second_exc:
                self.logger.emit(LogLevel.ERROR, f"Recovery navigation failed: {second_exc}")
                return False

    def stop(self) -> None:
        if self._context:
            self._context.close()
            self._context = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        self.logger.emit(LogLevel.INFO, "Browser session stopped.")
