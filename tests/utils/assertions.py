from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from locators_module.base_page_locators import CONSTRUCTOR_TEXT
from locators_module.order_feed_locators import ORDER_TAPE_TEXT


def assert_constructor_text(driver, expected_text: str, timeout: int = 5) -> bool:
    """
    Ждёт появления элемента с текстом внутри конструктора и возвращает True,
    иначе вызывает AssertionError.
    """
    locator = CONSTRUCTOR_TEXT
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
    element = driver.find_element(*locator)
    assert expected_text in element.text
    return True

def assert_order_tape_text(driver, expected_text: str, timeout: int = 5) -> bool:
    locator = ORDER_TAPE_TEXT
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
    element = driver.find_element(*locator)
    assert expected_text in element.text
    return True