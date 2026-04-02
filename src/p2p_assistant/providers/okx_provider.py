from p2p_assistant.providers.base import ExchangeProvider


class OKXProvider(ExchangeProvider):
    platform_name = "OKX"

    def is_logged_in(self, page):
        raise NotImplementedError

    def open_login(self, page):
        raise NotImplementedError

    def iter_filtered_order_links(self, listing_page):
        raise NotImplementedError

    def goto_numeric_page(self, listing_page, target_page_number: int):
        raise NotImplementedError

    def scrape_order_detail(self, context, detail_url: str, exchange_account: str):
        raise NotImplementedError
