from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from playwright.sync_api import BrowserContext, Page

from p2p_assistant.core.models import ChatMessage, OrderRecord


class ExchangeProvider(ABC):
    platform_name: str

    @abstractmethod
    def is_logged_in(self, page: Page) -> bool:
        raise NotImplementedError

    @abstractmethod
    def open_login(self, page: Page) -> None:
        raise NotImplementedError

    @abstractmethod
    def iter_filtered_order_links(self, listing_page: Page) -> Iterable[str]:
        raise NotImplementedError

    @abstractmethod
    def goto_numeric_page(self, listing_page: Page, target_page_number: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def scrape_order_detail(self, context: BrowserContext, detail_url: str, exchange_account: str) -> tuple[OrderRecord, List[ChatMessage]]:
        raise NotImplementedError
