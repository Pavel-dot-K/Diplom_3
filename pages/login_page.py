from __future__ import annotations
import allure
from pages.base_page import BasePage
from locators_module import login_page_locators 
from locators_module import base_page_locators


class LoginPage(BasePage):


    def open_login(self, base_url: str) -> "LoginPage":
        with allure.step("Открыть страницу логина"):
            self.open(base_url.rstrip("/") + "/login")
        with allure.step("Ожидать видимость ссылки регистрации"):
            self.wait_visible(login_page_locators.REGISTER_LINK)
        return self


    def fill_credentials_and_submit(self, email: str, password: str) -> "LoginPage":
        with allure.step(f"Ввести email: {email}"):
            self.type(login_page_locators.EMAIL_INPUT, email)
        with allure.step("Ввести пароль"):
            self.type(login_page_locators.PASSWORD_INPUT, password)
        with allure.step("Нажать кнопку входа"):
            self.click(login_page_locators.ENTER_BUTTON)
        return self


    def wait_logged_in(self) -> "LoginPage":
        with allure.step("Ожидание завершения входа"):
            self.wait_gone(login_page_locators.ENTER_BUTTON)
        with allure.step("Ожидание видимости конструктора на главной странице"):
            self.wait_visible(base_page_locators.CONSTRUCTOR_TEXT)
        return self


    def login(self, base_url: str, email: str, password: str) -> "LoginPage":
        with allure.step("Полный процесс входа: открыть логин, ввести креды и ждать вход"):
            return (
                self.open_login(base_url)
                    .fill_credentials_and_submit(email, password)
                    .wait_logged_in()
            )