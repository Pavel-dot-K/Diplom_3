import allure
import pytest
from data.url import Urls
from pages.main_page import MainPage
from pages.order_feed_page import OrderFeedPage


@pytest.mark.usefixtures("auth_login")


class TestOrderFeed:


    @allure.title("Увеличение общего времени в ленте после оформления заказа")
    @allure.feature("Лента заказов: подсчет времени")
    @allure.story("Проверка увеличения общего времени после оформления заказа")
    def test_increase_total_time_counter(self, driver):
        feed = (
            OrderFeedPage(driver)
            .open_feed(Urls.ORDER_PAGE)
            .wait_load()
            .scroll_to_counters()
        )

        with allure.step("Получить текущее значение общего времени"):
            before_all = feed.total_all_time()

        with allure.step("Собрать бургер и оформить заказ"):
            main = MainPage(driver).open(Urls.BASE_URL)
            main.build_burger_with_drag_and_drop()
            assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна"
            assert main.try_get_order_number_from_modal(), "Не получили номер"
            main.close_ingredient_modal()

        with allure.step("Обновить ленту и проверить увеличение общего времени"):
            feed.open_feed(Urls.ORDER_PAGE).wait_load()

        with allure.step("Проверка, что общее время увеличилось"):
            increased = feed.total_counter_increased(before_all, timeout=20)
            assert increased, f"'За всё время' не вырос"

    @allure.title("Увеличение счетчика за сегодня в ленте после оформления заказа")
    @allure.feature("Лента заказов: подсчет времени")
    @allure.story("Проверка увеличения счетчика за сегодня после оформления заказа")
    def test_counter_increase_today(self, driver):
        feed = (
            OrderFeedPage(driver)
            .open_feed(Urls.ORDER_PAGE)
            .wait_load()
            .scroll_to_counters()
        )

        with allure.step("Получить текущее значение за сегодня"):
            before_today = feed.total_today()

        with allure.step("Собрать бургер и оформить заказ"):
            main = MainPage(driver).open(Urls.BASE_URL)
            main.build_burger_with_drag_and_drop()
            assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна"
            assert main.try_get_order_number_from_modal(), "Не получили номер"
            main.close_ingredient_modal()

        with allure.step("Обновить ленту и проверить увеличение счетчика за сегодня"):
            feed.open_feed(Urls.ORDER_PAGE).wait_load()

        with allure.step("Проверка, что счётчик за сегодня увеличился"):
            increased = feed.today_counter_increased(before_today, timeout=20)
            assert increased, f"'За сегодня' не вырос"

    @allure.title("Проверка номера заказа в ленте после оформления")
    @allure.feature("Лента заказов: оформление и отображение номера заказа")
    @allure.story("После оформления номер заказа появляется в ленте и совпадает с заказом из окна")
    def test_order_number_in_progress(self, driver):
        feed = OrderFeedPage(driver).open_feed(Urls.ORDER_PAGE).wait_load()
        with allure.step("Перейти на базовую страницу и оформить бургер"):
            main = MainPage(driver).open(Urls.BASE_URL)
            main.build_burger_with_drag_and_drop()
            assert main.place_order_if_enabled(), "Кнопка 'Оформить заказ' недоступна"
            order_number = (main.try_get_order_number_from_modal() or "").strip()
            assert order_number, "Не получили номер заказа из окна"

        with allure.step("Открыть ленту и найти номер заказа в ленте"):
            feed = OrderFeedPage(driver).open_feed(Urls.ORDER_PAGE).wait_load()
            order_tape_number_text = feed.find_order_tape_number(order_number)

        with allure.step("Проверить соответствие номера в ленте"):
            expected = "#" + order_number.strip().lstrip("#")
            assert order_tape_number_text == expected, (
                f"Ожидалось {expected}, но найдено {order_tape_number_text}"
            )