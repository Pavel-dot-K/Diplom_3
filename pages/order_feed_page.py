from __future__ import annotations
import re
import allure
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


    @allure.step("Получить набор текстов по локатору: {locator}")
    def _get_texts_set(self, locator) -> set[str]:
        return {
            (el.text or "").strip()
            for el in self.finds(locator)
            if (el.text or "").strip()
        }

    @allure.step("Открыть фид заказов: {base_url}")
    def open_feed(self, base_url: str) -> "OrderFeedPage":
        self.open(base_url)
        return self

    @allure.step("Дождаться загрузки страницы фида заказов")
    def wait_load(self) -> "OrderFeedPage":
        with allure.step("Ожидание видимости основных элементов"):
            self.wait_any_visible(
                order_feed_locators.HEADER_IN_PROGRESS,
                order_feed_locators.TOTAL_ALL_TIME,
                order_feed_locators.HEADER_READY,
            )
        return self

    @allure.step("Прокрутить до блока со счётчиками")
    def scroll_to_counters(self) -> "OrderFeedPage":
        target = order_feed_locators.HEADER_READY if self.is_visible(order_feed_locators.HEADER_READY) else order_feed_locators.HEADER_IN_PROGRESS
        with allure.step(f"Цель прокрутки: {target}"):
            self.scroll_into_view(target)
        return self

    @allure.step("Получить общее количество 'Выполнено за всё время'")
    def total_all_time(self) -> int:
        el = self.wait_visible(order_feed_locators.TOTAL_ALL_TIME)
        with allure.step(f"Текст элемента: {el.text!r}"):
            return _to_int_safe(el.text)

    @allure.step("Получить количество 'Выполнено за сегодня'")
    def total_today(self) -> int:
        el = self.wait_visible(order_feed_locators.TOTAL_TODAY)
        with allure.step(f"Текст элемента: {el.text!r}"):
            return _to_int_safe(el.text)

    @allure.step("Проверить, есть ли заказ в работе: {order_number}")
    def has_order_in_progress(self, order_number: str) -> bool:
        return order_number.strip() in self._get_texts_set(order_feed_locators.HEADER_IN_PROGRESS)

    @allure.step("Получить номера заказов в работе")
    def get_in_progress_numbers(self) -> set[str]:
        return self._get_texts_set(order_feed_locators.IN_WORK_NUMBER_BLOCK)

    @allure.step("Получить номера готовых заказов")
    def get_ready_numbers(self) -> set[str]:
        return self._get_texts_set(order_feed_locators.HEADER_READY)

    @allure.step("Ожидать увеличения счётчика 'Выполнено за сегодня' (до > {before})")
    def today_counter_increased(self, before: int, timeout: int = 20) -> bool:
        self.scroll_to_counters()
        with allure.step(f"Ожидание увеличения today > {before}, таймаут {timeout}s"):
            self.wait_until(
                lambda: self.total_today() > before,
                timeout=timeout,
                message=f"'Выполнено за сегодня' не выросло",
            )
        return self.total_today() > before

    @allure.step("Ожидать увеличения счётчика 'Выполнено за всё время' (до > {before})")
    def total_counter_increased(self, before: int, timeout: int = 20) -> bool:
        self.scroll_to_counters()
        with allure.step(f"Ожидание увеличения total_all_time > {before}, таймаут {timeout}s"):
            self.wait_until(
                lambda: self.total_all_time() > before,
                timeout=timeout,
                message=f"'Выполнено за всё время' не выросло",
            )
        return self.total_all_time() > before

    @allure.step("Найти номер заказа в ленте: {order_number}")
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

        with allure.step(f"Ожидаем видимости элемента по XPATH: {xpath}"):
            el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
        with allure.step(f"Найден текст: {el.text!r}"):
            return el.text.strip()