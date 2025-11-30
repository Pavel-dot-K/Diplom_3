from __future__ import annotations
import time
import allure
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
    StaleElementReferenceException,
    ElementNotInteractableException
)
from selenium.webdriver import ActionChains



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
        with allure.step(f"_normalize_locator(locator={locator})"):
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
        with allure.step(f"Инициализация: timeout={timeout}"):
            self.driver = driver
            self._default_timeout = timeout


    def open(self, url: str):
        with allure.step(f"Открыть страницу: url={url}"):
            self.driver.get(url)
            return self
    

    def js_click(self, element: WebElement):
        with allure.step("JS-клик по элементу"):
                self.driver.execute_script("arguments[0].click();", element)


    def find(self, locator: Locator) -> WebElement:
        with allure.step(f"Найти элемент: locator={locator}"):
            return self.driver.find_element(*locator)


    def finds(self, locator) -> List[WebElement]:
        with allure.step(f"Найти элементы: locator={locator}"):
            if isinstance(locator, tuple) and len(locator) == 2:
                by, loc = locator
                return self.driver.find_elements(by, loc)
            if isinstance(locator, str):
                return self.driver.find_elements(By.CSS_SELECTOR, locator)
            return self.driver.find_elements(*locator)
    

    def open_ingredient_modal(self) -> None:
        with allure.step("Открыть ингредиент- модальное окно"):
            self.click(base_page_locators.BUN_BUTTON)


    def scroll_to_top(self) -> None:
        with allure.step("Прокрутить страницу вверх"):
            with suppress(Exception):
                self.driver.execute_script("window.scrollTo(0, 0);")


    def click(self, locator, timeout=6):
        with allure.step(f"Клик по элементу: locator={locator}, timeout={timeout}"):
            try:
                WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
                self.driver.find_element(*locator).click()
            except ElementClickInterceptedException:
                overlays = base_page_locators.OVERLAY
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
            

    # Функция без time.sleep, по комментарию # 7
    @allure.step("Безопасный клик: locator={locator}")
    def safe_click(self, locator) -> None:
        last_err: Optional[Exception] = None
        for _ in range(2):
                el = self.wait_visible(locator)
                self.scroll_into_view(el)
                self.wait_clickable(locator).click()
                return
        if last_err:
                raise last_err
        with suppress(Exception):
            self.close_overlays_if_any()
            self.scroll_to_top()
                                    

    def wait_clickable(self, locator):
        with allure.step(f"Ожидание кликабельности"):
            return self.wait.until(EC.element_to_be_clickable(locator))


    def wait_until(self, condition: Callable, timeout: Optional[int] = None, message: Optional[str] = None):
        t = self._default_timeout if timeout is None else timeout
        with allure.step(f"Wait until: timeout={timeout}, message={message}"):
            tw = self.wait if timeout is None else WebDriverWait(self.driver, timeout, poll_frequency=DEFAULT_POLL)
            def _cond(driver=None):
                try:
                    return condition(driver)
                except TypeError:
                    return condition()
            return tw.until(_cond, message)
    

    def wait_gone(self, locator) -> bool:
        with allure.step(f"Wait gone: locator={locator}"):
            with suppress(TimeoutException):
                return bool(self.wait.until(EC.invisibility_of_element_located(locator)))
            return False


    def wait_visible(self, locator, timeout: int = None) -> WebElement:
        t = timeout if timeout is not None else self._default_timeout
        with allure.step(f"Wait visible: locator={locator}, timeout={timeout}"):
            if isinstance(locator, WebElement):
                return locator
            by, value = self._normalize_locator(locator)
            return WebDriverWait(self.driver, t).until(
                EC.visibility_of_element_located((by, value))
            )


    def _element_is_descendant(self, parent, child) -> bool:
        with allure.step("Проверить, является ли элемент потомком"):
            try:
                return self.driver.execute_script("return arguments[0].contains(arguments[1]);", parent, child)
            except Exception:
                return False


    def is_present(self, locator) -> bool:
        with allure.step(f"Проверка наличия элемента: locator={locator}"):
            try:
                self.wait.until(EC.presence_of_element_located(locator))
                return True
            except Exception:
                return False


    @property
    def modal_overlay_present(self) -> bool:
        with allure.step("Проверить наличие modal overlay"):
            overlays = self.finds(base_page_locators.MODAL_OVERLAY)
            return bool(overlays)


    def close_overlays_if_any(self) -> None:
        with allure.step("Закрыть попапы/оверлеи при наличии"):
            if self.modal_overlay_present:
                overlays = self.driver.find_elements(*base_page_locators.MODAL_OVERLAY)
                if overlays:
                    close_btns = self.driver.find_elements(*base_page_locators.INGREDIENT_MODAL_CLOSE)
                    if close_btns:
                        self.js_click(close_btns[0])
        self.is_ingredient_modal_absent(timeout=5)


    def open(self, url: str) -> "MainPage":
        with allure.step(f"Open page: url={url}"):
            self.get(url)
            return self
    

    def scroll_into_view(self, target: MaybeEl, block: str = 'center') -> None:
        with allure.step("Прокрутить до элемента в видимую область"):
            el = self._as_element(target)
            with suppress(Exception):
                self.execute_script_view(
                    "arguments[0].scrollIntoView({block: arguments[1]});",
                    el,
                    block
                )


    def execute_script_view(self, script, *args):
        with allure.step("Обёртка над WebDriver.execute_script_view"):
            return self.driver.execute_script(script, *args)


    def type(self, locator, text, timeout: int = 10):
        with allure.step(f"Ввод текста в элемент: locator={locator}, текст={text!r}, timeout={timeout}"):
            element = self.wait_visible(locator, timeout)
            element.clear()
            element.send_keys(text)
            return self
    

    def wait_gone(self, locator, timeout=10) -> bool:
        with allure.step(f"Wait element gone: locator={locator}, timeout={timeout}"):
            with suppress(TimeoutException):
                return bool(self.wait_until_invisible(locator, timeout))
            return False


    def wait_any_visible(self, *locators, timeout: int = 15) -> WebElement:
        with allure.step(f"Wait any visible: locators={locators}, timeout={timeout}"):
            t = timeout
            conditions = [
                EC.visibility_of_element_located(self._normalize_locator(l))
                if isinstance(l, tuple) else EC.visibility_of_element_located(l)
                for l in locators
            ]
            return WebDriverWait(self.driver, t).until(EC.any_of(*conditions))
    

    def wait_until_invisible(self, locator, timeout=None):
        def condition(driver):
            by, value = self._normalize_locator(locator)
            return EC.invisibility_of_element_located((by, value))(driver)
        return self.wait_until(condition, timeout=timeout, message=f"Ожидание исчезновения элемента: {locator}")


    def is_visible(self, locator, timeout=5) -> bool:
        with allure.step(f"Check visibility: locator={locator}, timeout={timeout}"):
            try:
                def condition(driver):
                    by, value = self._normalize_locator(locator)
                    return EC.visibility_of_element_located((by, value))(driver)

                self.wait_until(condition, timeout=timeout)
                return True
            except TimeoutException:
                return False
        

    def _as_element(self, maybe: MaybeEl) -> WebElement:
        with allure.step(f"Convert to WebElement: target={maybe}"):
            if isinstance(maybe, WebElement):
                return maybe
            if isinstance(maybe, tuple) and len(maybe) == 2:
                by, locator = maybe
                return self.find((by, locator))
            if isinstance(maybe, str):
                return self.find((By.CSS_SELECTOR, maybe))
            raise TypeError(f"Unsupported target type for _as_element: {type(maybe)}")
    

    def wait_invisible(self, locator, timeout: int = 15):
        with allure.step(f"Wait invisible: locator={locator}, timeout={timeout}"):
            by, value = self._normalize_locator(locator)
            return self.wait_until(
                lambda driver: EC.invisibility_of_element_located((by, value))(driver),
                timeout=timeout,
                message=f"Waiting for invisibility of element located by {locator}"
            )


    def click_with_fallbacks(self,
                         locator: tuple,
                         timeout_clickable: float = 5,
                         timeout_presence: float = 5,
                         attach_on_failure: bool = True) -> bool:
        """
        Стратегии: wait clickable -> native click
                 -> ActionChains -> JS click via presence
        Возвращает True если клик успешен, иначе False.
        """
        el = None
        try:
            with allure.step(f"click_with_fallbacks: wait clickable {locator}"):
                el = self.wait_clickable(locator, timeout=timeout_clickable)
                el.click()
                return True
        except (ElementClickInterceptedException, ElementNotInteractableException,
                StaleElementReferenceException, TimeoutException) as first_err:
            # ActionChains
            try:
                with allure.step(f"click_with_fallbacks: ActionChains for {locator}"):
                    el = self.find(locator, timeout=timeout_presence)
                    ActionChains(self.driver).move_to_element(el).click().perform()
                    return True
            except Exception:
                pass
            # JS click via presence
            try:
                with allure.step(f"click_with_fallbacks: JS click for {locator}"):
                    el = self.wait_presence(locator, timeout=timeout_presence)
                    self.scroll_into_view(el)
                    self.js_click_element(el)
                    return True
            except Exception:
                # attach diagnostics
                if attach_on_failure:
                    with suppress(Exception):
                        if el is not None:
                            try:
                                allure.attach(el.get_attribute("outerHTML"), name="element_outerHTML", attachment_type=allure.attachment_type.HTML)
                            except Exception:
                                pass
                        self.attach_screenshot("click_failure")
                return False
        except Exception:
            return False
        

    def execute_script(self, script: str, *args):
        with allure.step("Обёртка над WebDriver.execute_script"):
            return self.driver.execute_script(script, *args)


    def js_drag_and_drop(self, source_el, target_el):
        with allure.step("Выполнить drag-and-drop через JS"):
            script = """
            var s = arguments[0], t = arguments[1];
            function fire(el, type, dt){
                var e = document.createEvent('CustomEvent');
                e.initCustomEvent(type, true, true, null);
                e.dataTransfer = dt;
                el.dispatchEvent(e);
            }
            var dt = {
                data: {},
                setData: function(k,v){this.data[k]=v},
                getData: function(k){return this.data[k]}
            };
            fire(s,'dragstart',dt);
            fire(t,'dragenter',dt);
            fire(t,'dragover',dt);
            fire(t,'drop',dt);
            fire(s,'dragend',dt);
            """
            self.execute_script(script, source_el, target_el)


    def get(self, url: str):
        with allure.step(f"Открыть страницу: {url}"):
            self.driver.get(url)