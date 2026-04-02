from __future__ import annotations

from typing import List

from p2p_assistant.core.enums import LogLevel
from p2p_assistant.core.logging_service import LoggingService
from p2p_assistant.core.models import OrderRecord
from p2p_assistant.parsing.chat_parser import ChatPaymentParser
from p2p_assistant.providers.base import ExchangeProvider


class ReviewService:
    def __init__(self, provider: ExchangeProvider, logger: LoggingService) -> None:
        self.provider = provider
        self.logger = logger
        self.parser = ChatPaymentParser()

    def run(self, context, listing_page, exchange_account: str, max_pages: int = 100) -> List[OrderRecord]:
        orders: List[OrderRecord] = []
        current_page = 1

        while current_page <= max_pages:
            self.logger.emit(LogLevel.INFO, f"Review page {current_page}")
            links = list(dict.fromkeys(self.provider.iter_filtered_order_links(listing_page)))
            if not links:
                self.logger.emit(LogLevel.WARNING, "No orders detected on current page.")

            total = len(links)
            self.logger.emit(LogLevel.INFO, f"Detected {total} orders on page {current_page}")

            for i, detail_url in enumerate(links, start=1):
                self.logger.emit(LogLevel.INFO, f"Order {i}/{total} opened")
                order, messages = self.provider.scrape_order_detail(context, detail_url, exchange_account)
                parsed = self.parser.parse(messages)
                order.parsed_payment = parsed
                order.reviewed = True
                self.logger.emit(LogLevel.INFO, f"Extracted account number: {parsed.account_number or 'N/A'}")
                orders.append(order)

            next_page = current_page + 1
            if not self.provider.goto_numeric_page(listing_page, next_page):
                self.logger.emit(LogLevel.SUCCESS, "No more numeric pages. Review completed.")
                break
            self.logger.emit(LogLevel.INFO, f"Moved to page {next_page}")
            current_page = next_page

        return orders
