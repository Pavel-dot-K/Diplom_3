import allure
from pages.main_page import MainPage
from data.url import Urls
from tests.utils.assertions import assert_constructor_text
from tests.utils.assertions import assert_order_tape_text


class TestFunctionality:


    @allure.title("Переходим из главной в конструктор через кнопку 'Конструктор' и проверяем текст конструктора")
    @allure.feature("Навигация: Главная → Конструктор")
    @allure.story("Переход к конструктору через кнопку на главной странице")
    def test_click_to_go_to_the_constructor(self, driver):
        page = MainPage(driver).open(Urls.BASE_URL)
        with allure.step("Перейти в ленту и затем в конструктор"):
            page.go_to_feed().go_to_constructor()
        with allure.step("Проверить текст конструктора"):
            assert_constructor_text(driver, "Соберите бургер")


    @allure.title("Переход в ленту и проверка заголовка ленты заказов")
    @allure.feature("Навигация: Конструктор → Лента заказов")
    @allure.story("Открыть ленту заказов из конструктора")
    def test_click_to_go_to_the_feed(self, driver):
        page = MainPage(driver).open(Urls.BASE_URL)
        with allure.step("Перейти в ленту заказов"):
            page.go_to_feed()
        with allure.step("Проверить заголовок ленты заказов"):
            assert_order_tape_text(driver, "Лента заказов")


    @allure.title("Открытие окна ингредиента при клике на bun")
    @allure.feature("Интерактивная работа с ингредиентами")
    @allure.story("Клик по булке открывает окно ингредиента")
    def test_click_bun_opens_ingredient_modal(self, driver):
        page = MainPage(driver) 
        with allure.step("Клик по булке"):
            page.click_bun()
        with allure.step("Проверить отображение окна ингредиента"):
            assert page.is_ingredient_modal_displayed(), "Окно не появилось после клика"


    @allure.title("Закрытие модального окна ингредиента через крестик")
    @allure.feature("Интерактивная работа с ингредиентами")
    @allure.story("Закрыть окно ингредиента")
    def test_click_cross_close_window(self, driver):
        page = MainPage(driver)
        with allure.step("Открыть окно ингредиента и проверить его отображение"):
            page.click_bun()
            assert page.is_ingredient_modal_displayed(), "Окно не появилось после клика"
        with allure.step("Закрыть окно модальным крестиком и проверить отсутствие окна"):
            page.close_ingredient_modal()
            assert page.is_ingredient_modal_absent(), "Окно с информацией об ингредиенте не закрыто"


    @allure.title("Перемещение булки в блок добавления и верификация номера заказа в ленте")
    @allure.feature("Перемещение ингредиента и проверка номера в ленте")
    @allure.story("Переместить bun в блок и проверить номер заказа в ленте после оформления")
    def test_move_bun_to_add_block_and_verify_number(self, driver):
        page = MainPage(driver)
        with allure.step("Переместить bun в блок добавления и проверить обновление номера"):
            assert page.move_bun_to_add_block_and_verify_number(), "Не удалось переместить ингредиент и проверить номер"