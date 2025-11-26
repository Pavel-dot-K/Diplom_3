from __future__ import annotations
import time
from contextlib import suppress
from typing import Tuple, Optional, Union, Callable
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from locators_module import base_page_locators
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)


Locator = Tuple[By, str]
MaybeEl = Union[Locator, WebElement, str]
DEFAULT_POLL = 0.2


BY_ALIAS = {
    'link text': By.LINK_TEXT,
    'xpath': By.XPATH,
    'css selector': By.CSS_SELECTOR,
    'css': By.CSS_SELECTOR,
    'id': By.ID,
    'name': By.NAME,
    'tag name': By.TAG_NAME,
    'class name': By.CLASS_NAME,
    'partial link text': By.PARTIAL_LINK_TEXT,
}


class BasePage:


    def _normalize_locator(self, locator):
        if isinstance(locator, tuple) and len(locator) == 2:
            by, value = locator
            if isinstance(by, str):
                mapped = BY_ALIAS.get(by.lower())
                if mapped:
                    return (mapped, value)
                if hasattr(By, by.upper()):
                    return (getattr(By, by.upper()), value)
                raise ValueError(f"Unsupported locator type: {by}")
            else:
                return (by, value)
        return locator


    def __init__(self, driver, timeout=15):
        self.driver = driver
        self._default_timeout = timeout


    def open(self, url: str):
        self.driver.get(url)
        return self
    

    def js_click(self, element: WebElement):
        self.driver.execute_script("arguments[0].click();", element)


    def find(self, locator: Locator) -> WebElement:
        return self.driver.find_element(*locator)


    def finds(self, locator) -> List[WebElement]:
        if isinstance(locator, tuple) and len(locator) == 2:
            by, loc = locator
            return self.driver.find_elements(by, loc)
        if isinstance(locator, str):
            return self.driver.find_elements(By.CSS_SELECTOR, locator)
        return self.driver.find_elements(*locator)
    

    def open_ingredient_modal(self) -> None:
        self.click(base_page_locators.FIRST_INGREDIENT_CARD)


    def scroll_to_top(self) -> None:
        with suppress(Exception):
            self.driver.execute_script("window.scrollTo(0, 0);")


    def click(self, locator, timeout=6):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
            self.driver.find_element(*locator).click()
        except ElementClickInterceptedException:
            overlays = [
                ("css selector", "div.Modal_modal_overlay__x2ZCr"),
                ("css selector", "div.Modal_modal_overlay"),
            ]
            for ol in overlays:
                try:
                    WebDriverWait(self.driver, 2).until(EC.invisibility_of_element_located(ol))
                except Exception:
                    pass 
            element = self.driver.find_element(*locator)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
            self.driver.execute_script("arguments[0].click();", element)
            return self
        except TimeoutException:
            raise


    def safe_click(self, locator: Locator) -> None:
        last_err: Optional[Exception] = None
        for _ in range(2):
            try:
                el = self.wait_visible(locator)
                self.scroll_into_view(el)
                self.wait_clickable(locator).click()
                return
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                last_err = e
                time.sleep(0.25)
                with suppress(Exception):
                    self.close_overlays_if_any()
                    self.scroll_to_top()
        with suppress(Exception):
            el = self.find(locator)
            self.scroll_into_view(el)
            self.js_click(el)
            return
        if last_err:
            raise last_err


    def wait_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    
    def wait_until(self, condition: Callable, timeout: Optional[int] = None, message: Optional[str] = None):
        t = self._default_timeout if timeout is None else timeout
        tw = self.wait if timeout is None else WebDriverWait(self.driver, timeout, poll_frequency=DEFAULT_POLL)
        def _cond(driver=None):
            try:
                return condition(driver)
            except TypeError:
                return condition()
        return tw.until(_cond, message)

    
    def wait_gone(self, locator: Locator) -> bool:
        with suppress(TimeoutException):
            return bool(self.wait.until(EC.invisibility_of_element_located(locator)))
        return False
    

    def wait_visible(self, locator, timeout: int = None) -> WebElement:
        t = timeout if timeout is not None else self._default_timeout
        if isinstance(locator, WebElement):
            return locator
        by, value = self._normalize_locator(locator)
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of_element_located((by, value))
        )

        
    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'nearest'});", element)


    def _element_is_descendant(self, parent, child) -> bool:
        try:
            return self.driver.execute_script("return arguments[0].contains(arguments[1]);", parent, child)
        except Exception:
            return False


    def is_present(self, locator) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located(locator))
            return True
        except Exception:
            return False


    @property
    def modal_overlay_present(self) -> bool:
        overlays = self.finds(base_page_locators.MODAL_OVERLAY)
        return bool(overlays)


    def close_overlays_if_any(self) -> None:
        if self.modal_overlay_present:
            overlays = self.driver.find_elements(*base_page_locators.MODAL_OVERLAY)
            if overlays:
                close_btns = self.driver.find_elements(*base_page_locators.INGREDIENT_MODAL_CLOSE)
                if close_btns:
                    self.js_click(close_btns[0])
        self.is_ingredient_modal_absent(timeout=5)


    def open(self, url: str) -> "MainPage":
        self.driver.get(url)
        return self
    

    def scroll_into_view(self, target: MaybeEl, block: str = 'center') -> None:
        el = self._as_element(target)
        with suppress(Exception):
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: arguments[1]});",
                el,
                block
            )


    def type(self, locator, text, timeout: int = 10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        element.clear()
        element.send_keys(text)
        return self
    

    def wait_gone(self, locator, timeout=10):
        from selenium.common.exceptions import TimeoutException
        from contextlib import suppress
        with suppress(TimeoutException):
            return bool(WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            ))
        return False
    

    def wait_any_visible(self, *locators, timeout: int = 15) -> WebElement:
        t = timeout
        conditions = [
            EC.visibility_of_element_located(self._normalize_locator(l))
            if isinstance(l, tuple) else EC.visibility_of_element_located(l)
            for l in locators
        ]
        return WebDriverWait(self.driver, t).until(EC.any_of(*conditions))
    

    def is_visible(self, locator, timeout=5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
        

    def _as_element(self, maybe: MaybeEl) -> WebElement:
        if isinstance(maybe, WebElement):
            return maybe
        if isinstance(maybe, tuple) and len(maybe) == 2:
            by, locator = maybe
            return self.driver.find_element(by, locator)
        if isinstance(maybe, str):
            return self.driver.find_element(By.CSS_SELECTOR, maybe)
        raise TypeError(f"Unsupported target type for _as_element: {type(maybe)}")
    

    def wait_invisible(self, locator, timeout: int = 15):
        by, value = self._normalize_locator(locator)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((by, value))
        )