import pytest
import tempfile
import os
import importlib.util as util
from importlib import import_module
from selenium import webdriver
from data.url import Urls
from pages.login_page import LoginPage

# Загрузка учетных данных заранее
_FILE_EMAIL = _FILE_PASSWORD = None
if util.find_spec("data.test_data") is not None:
    creds = import_module("data.test_data")
    _FILE_EMAIL = getattr(creds, "STELLAR_EMAIL", None)
    _FILE_PASSWORD = getattr(creds, "STELLAR_PASSWORD", None)

@pytest.fixture(params=["firefox", "chrome"])
def driver(request):
    browser_name = request.param
    driver = None
    try:
        if browser_name == "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            driver = webdriver.Firefox(options=options)
        elif browser_name == "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            temp_dir = tempfile.mkdtemp()
            options.add_argument(f"--user-data-dir={temp_dir}")
            driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        driver.get(Urls.BASE_URL)
        yield driver
    finally:
        if driver:
            driver.quit()


@pytest.fixture
def auth_login(driver):
    email = _FILE_EMAIL or os.getenv("STELLAR_EMAIL")
    password = _FILE_PASSWORD or os.getenv("STELLAR_PASSWORD")
    if not (email and password):
        pytest.skip("Нет учётных данных")
    LoginPage(driver).login(Urls.BASE_URL, email, password)
    yield