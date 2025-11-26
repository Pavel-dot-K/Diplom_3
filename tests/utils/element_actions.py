from typing import List, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_visibility(
    driver: WebDriver,
    by: By,
    locator: str,
    timeout: int = 10,
    poll_frequency: float = 0.2
):
    """
    Ожидает видимость элемента.
    """
    return WebDriverWait(driver, timeout, poll_frequency=poll_frequency).until(
        EC.visibility_of_element_located((by, locator))
    )


def wait_for_clickable(
    driver: WebDriver,
    by: By,
    locator: str,
    timeout: int = 10,
    poll_frequency: float = 0.2
):
    """
    Ожидает кликабельность элемента.
    """
    return WebDriverWait(driver, timeout, poll_frequency=poll_frequency).until(
        EC.element_to_be_clickable((by, locator))
    )


def safe_click(
    driver: WebDriver,
    by: By,
    locator: str,
    timeout: int = 10,
    scroll_into_view: bool = True,
    use_js: bool = False
):
    """
    Безопасный клик по элементу:
    - при необходимости прокручиваем к элементу
    - пробуем обычный click, если не получилось — клик через JS
    """
    elem = wait_for_clickable(driver, by, locator, timeout)
    if scroll_into_view:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
    try:
        elem.click()
    except Exception:
        if use_js:
            driver.execute_script("arguments[0].click();", elem)
        else:
            raise
    return elem


def find_and_click_any(
    driver: WebDriver,
    locators: List[Tuple[By, str]],
    timeout_per_locator: int = 5,
    overall_timeout: int = 10
):
    """
    Пытается кликнуть по первому из набора локаторов.
    Возвращает найденный элемент и кликает по нему.
    """
    import time
    end_time = time.time() + overall_timeout
    last_err = None

    while time.time() < end_time:
        for by, locator in locators:
            try:
                elem = wait_for_clickable(driver, by, locator, timeout_per_locator)
                elem.click()
                return elem
            except Exception as e:
                last_err = e
                continue
        time.sleep(0.2)

    raise RuntimeError(f"Element not clickable after {overall_timeout}s. Last error: {last_err}")