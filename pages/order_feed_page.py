from __future__ import annotations
import re
from pages.base_page import BasePage
from locators_module import order_feed_locators
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def _to_int_safe(txt: str) -> int:
    return int(re.sub(r"\D", "", txt or "") or 0)


class OrderFeedPage(BasePage):


    def __init__(self, driver):
        super().__init__(driver)


    def _get_texts_set(self, locator) -> set[str]:
        return {
            (el.text or "").strip()
            for el in self.finds(locator)
            if (el.text or "").strip()
        }

 
    def open_feed(self, base_url: str) -> OrderFeedPage:
        self.open(base_url)
        return self


    def wait_load(self) -> OrderFeedPage:
        self.wait_any_visible(
            order_feed_locators.HEADER_IN_PROGRESS,
            order_feed_locators.ORDER_NUMBER,
            order_feed_locators.HEADER_READY,
        )
        return self


    def scroll_to_counters(self) -> OrderFeedPage:
        target = order_feed_locators.HEADER_READY if self.is_visible(order_feed_locators.HEADER_READY) else order_feed_locators.HEADER_IN_PROGRESS
        self.scroll_into_view(target)
        return self


    def total_all_time(self) -> int:
        el = self.wait_visible(order_feed_locators.TOTAL_ALL_TIME)
        return _to_int_safe(el.text)


    def total_today(self) -> int:
        el = self.wait_visible(order_feed_locators.TOTAL_TODAY)
        return _to_int_safe(el.text)


    def has_order_in_progress(self, order_number: str) -> bool:
        return order_number.strip() in self._get_texts_set(order_feed_locators.HEADER_IN_PROGRESS)


    def get_in_progress_numbers(self) -> set[str]:
        return self._get_texts_set(order_feed_locators.IN_WORK_NUMBER_BLOCK)


    def get_ready_numbers(self) -> set[str]:
        return self._get_texts_set(order_feed_locators.HEADER_READY)


    def today_counter_increased(self, before: int, timeout: int = 20) -> bool:
        self.scroll_to_counters()
        self.wait_until(
            lambda: self.total_today() > before,
            timeout=timeout,
            message=f"'Выполнено за сегодня' не выросло",
        )
        return self.total_today() > before


    def total_counter_increased(self, before: int, timeout: int = 20) -> bool:
        self.scroll_to_counters()
        self.wait_until(
            lambda: self.total_all_time() > before,
            timeout=timeout,
            message=f"'Выполнено за всё время' не выросло",
        )
        return self.total_all_time() > before
 

    def find_order_tape_number(self, order_number: str) -> str:
        if not order_number:
            raise ValueError("order_number must be non-empty")
        target = order_number.strip()
        if not target.startswith("#"):
            target = f"#{target}"
        xpath = (
            '//p[contains(@class, "text") and contains(@class, "text_type_digits-default") '
            'and normalize-space(.) = "{}"]'.format(target)
        )
        el = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        return el.text.strip()
    