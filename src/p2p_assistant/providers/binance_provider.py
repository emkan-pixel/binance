from __future__ import annotations

import re
from decimal import Decimal
from typing import Iterable, List

from playwright.sync_api import BrowserContext, Page

from p2p_assistant.core.models import ChatMessage, OrderRecord
from p2p_assistant.providers.base import ExchangeProvider


class BinanceProvider(ExchangeProvider):
    platform_name = "BINANCE"

    LOGIN_URL = "https://accounts.binance.com/en/login"
    ALL_ORDERS_URL = "https://p2p.binance.com/en/fiatOrder?tab=1&page=1"

    def is_logged_in(self, page: Page) -> bool:
        url = page.url.lower()
        if "login" in url:
            return False
        return "binance.com" in url

    def open_login(self, page: Page) -> None:
        page.goto(self.LOGIN_URL, wait_until="domcontentloaded")

    def iter_filtered_order_links(self, listing_page: Page) -> Iterable[str]:
        anchors = listing_page.locator("a[href*='fiatOrderDetail?orderNo=']")
        for i in range(anchors.count()):
            href = anchors.nth(i).get_attribute("href")
            if not href:
                continue
            if href.startswith("http"):
                yield href
            else:
                yield f"https://c2c.binance.com{href}"

    def goto_numeric_page(self, listing_page: Page, target_page_number: int) -> bool:
        locator = listing_page.locator(f"text='{target_page_number}'")
        if locator.count() == 0:
            return False
        locator.first.click()
        listing_page.wait_for_load_state("domcontentloaded")
        return True

    def scrape_order_detail(self, context: BrowserContext, detail_url: str, exchange_account: str) -> tuple[OrderRecord, List[ChatMessage]]:
        page = context.new_page()
        try:
            page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)

            full_text = page.locator("body").inner_text()
            order_id = self._extract_order_id(detail_url, full_text)
            amount_raw = self._extract_by_label(full_text, ["Fiat amount", "Amount"]) or "0"
            currency = self._extract_currency(amount_raw)

            order = OrderRecord(
                platform=self.platform_name,
                exchange_account=exchange_account,
                order_id=order_id,
                status=self._extract_by_label(full_text, ["Status"]) or "UNKNOWN",
                order_type=self._extract_by_label(full_text, ["Type"]),
                fiat_amount_raw=amount_raw,
                fiat_amount_normalized=self._normalize_amount(amount_raw),
                fiat_currency=currency,
                unit_price_raw=self._extract_by_label(full_text, ["Price"]),
                quantity_raw=self._extract_by_label(full_text, ["Total Quantity", "Quantity"]),
                fee_raw=self._extract_by_label(full_text, ["Fee"]),
                payment_method=self._extract_by_label(full_text, ["Payment method"]),
                detail_url=detail_url,
            )
            messages = self._scrape_chat(page, order_id)
            return order, messages
        finally:
            page.close()

    def _scrape_chat(self, page: Page, order_id: str) -> List[ChatMessage]:
        messages: List[ChatMessage] = []
        items = page.locator("[class*='chat'], [class*='message']")
        for i in range(min(items.count(), 300)):
            row = items.nth(i)
            text = row.inner_text().strip()
            img = row.locator("img").first
            image_url = img.get_attribute("src") if img.count() else None
            lowered = text.lower()
            sender = "system" if "system" in lowered else "counterparty"
            if "you" in lowered or "me" in lowered:
                sender = "mine"
            msg_type = "image" if image_url else "text"
            messages.append(ChatMessage(order_id=order_id, timestamp=None, sender=sender, text=text, image_url=image_url, message_type=msg_type))
        return messages

    def _extract_by_label(self, text: str, labels: list[str]) -> str | None:
        for label in labels:
            pattern = rf"{re.escape(label)}\s*[:\n]\s*([^\n]+)"
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _extract_currency(self, amount_text: str) -> str:
        m = re.search(r"\b([A-Z]{3})\b", amount_text)
        return m.group(1) if m else "UNKNOWN"

    def _normalize_amount(self, amount_text: str) -> Decimal:
        cleaned = re.sub(r"[^0-9.\-]", "", amount_text)
        if not cleaned:
            return Decimal("0")
        try:
            return Decimal(cleaned)
        except Exception:
            return Decimal("0")

    def _extract_order_id(self, detail_url: str, text: str) -> str:
        m = re.search(r"orderNo=([0-9]+)", detail_url)
        if m:
            return m.group(1)
        m2 = re.search(r"Order\s*(ID|number)?\s*[:\n]\s*([0-9]+)", text, re.IGNORECASE)
        if m2:
            return m2.group(2)
        return "UNKNOWN"
