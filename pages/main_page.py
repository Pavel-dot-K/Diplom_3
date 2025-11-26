# pages/main_page.py

from __future__ import annotations
import time
from typing import Tuple, Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from locators_module import base_page_locators
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
from tests.utils import element_actions
from pages.base_page import BasePage
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, MoveTargetOutOfBoundsException


Locator = Tuple[By, str]
MaybeEl = Union[Locator, WebElement, str]


class MainPage(BasePage):  


    def __init__(self, driver, timeout=15):
        super().__init__(driver, timeout)


    def close_ingredient_modal(self) -> None:
        self.close_overlays_if_any()
        if self.is_ingredient_modal_absent(timeout=2):
            return
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(base_page_locators.INGREDIENT_MODAL_CLOSE)
            )
            btn.click()
        except Exception:
            try:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(base_page_locators.INGREDIENT_MODAL_CLOSE)
                )
                self.driver.execute_script("arguments[0].click();", btn)
            except Exception:
                pass
        self.is_ingredient_modal_absent(timeout=15)   


    def _normalize_locators(self, first_locator):
        normalized = []
        if isinstance(first_locator, tuple) and len(first_locator) == 2:
            normalized.append(first_locator)
        elif isinstance(first_locator, (list, tuple)):
            for item in first_locator:
                if isinstance(item, tuple) and len(item) == 2:
                    normalized.append(item)
        return normalized


    def __init__(self, driver, timeout=15):
        self.driver = driver
        self._default_timeout = timeout
        self.wait = WebDriverWait(driver, timeout)


    def _click_first_available(self, locators, timeout: int = 10) -> bool:
        for by, locator in locators:
            try:
                btn = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, locator))
                )
                btn.click()
                return True
            except Exception:
                continue
        return False


    def click_bun(self, timeout=10) -> bool:
        bun_locators = [
            base_page_locators.BUN,         
            base_page_locators.BUNS_SECTION, 
            (By.XPATH, "//button[contains(., 'Булка')]"),
            (By.XPATH, "//button[contains(., 'BUN')]"),
        ]
        for by, locator in bun_locators:
            try:
                elem = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, locator))
                )
                elem.click()
                return True
            except Exception:
                continue
        raise RuntimeError("BUN button not found with any selector")


    @property
    def modal_overlay_present(self) -> bool:
        overlays = self.driver.find_elements(*base_page_locators.MODAL_OVERLAY)
        return bool(overlays)


    def wait_for_ingredient_modal(self, timeout: int = 10) -> bool:
        modal_locators = [
            base_page_locators.INGREDIENT_MODAL,                 # (By, locator)
            (By.CSS_SELECTOR, "div.IngredientModal"),
            (By.CSS_SELECTOR, "div.modal-ingredients"),
        ]
        for by, locator in modal_locators:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, locator))
                )
                return True
            except Exception:
                continue
        raise RuntimeError("INGREDIENT_MODAL did not appear")


    def is_ingredient_modal_displayed(self) -> bool:
        els = self.driver.find_elements(*base_page_locators.INGREDIENT_MODAL)
        return bool(els) and els[0].is_displayed()


    def is_ingredient_modal_absent(self, timeout: int = 5) -> bool:
        locators = [
            base_page_locators.INGREDIENT_MODAL,
            (By.CSS_SELECTOR, "div.IngredientModal"),
            (By.CSS_SELECTOR, "div.modal-ingredients"),
        ]
        end_time = time.time() + timeout
        while time.time() < end_time:
            any_visible = False
            for by, locator in locators:
                elements = self.driver.find_elements(by, locator)
                for el in elements:
                    try:
                        if el.is_displayed():
                            any_visible = True
                            break
                    except Exception:
                        continue
                if any_visible:
                    break
            if not any_visible:
                return True
            time.sleep(0.2)
        return False


    def close_overlays_if_any(self) -> None:
        if self.modal_overlay_present:
            btns = self.finds(base_page_locators.INGREDIENT_MODAL_CLOSE)
            if btns:
                self.js_click(btns[0])
            end_time = time.time() + 5
            while time.time() < end_time:
                self.finds(base_page_locators.INGREDIENT_MODAL)
                break
                time.sleep(0.2)
            return
        self.is_ingredient_modal_absent(timeout=15)


    def go_to_feed(self, timeout: int = 10) -> "MainPage":
        feed_locators = self._normalize_locators(base_page_locators.ORDER_TAPE_TAB)
        feed_locators += [
            (By.CSS_SELECTOR, "a[href='/feed']"),
            (By.CSS_SELECTOR, "a.AppHeader_header__link__3D_hX[href='/feed']"),
            (By.XPATH, "//a[@href='/feed']"),
            (By.XPATH, "//a[contains(@href, '/feed')]"),
        ]
        end_time = time.time() + timeout
        last_exception = None
        while time.time() < end_time:
            for by, locator in feed_locators:
                try:
                    elem = element_actions.wait_for_clickable(self.driver, by, locator, timeout=2)
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                    try:
                        elem.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", elem)
                    return self
                except Exception as e:
                    last_exception = e
                    continue
            time.sleep(0.2)
        raise RuntimeError(f"Go to feed button not found after {timeout}s. Last exception: {last_exception}")


    def go_to_constructor(self, timeout: int = 10) -> "MainPage":
        constructor_locators = self._normalize_locators(base_page_locators.CONSTRUCTOR_TAB)
        constructor_locators += [
            (By.CSS_SELECTOR, "a[href='/constructor']"),
            (By.CSS_SELECTOR, "a[data-testid='constructor']"),
            (By.CSS_SELECTOR, "a[data-test='constructor']"),
            (By.XPATH, "//a[@href='/constructor']"),
            (By.XPATH, "//a[contains(@href, '/constructor')]"),
            (By.LINK_TEXT, "Конструктор"),
            (By.PARTIAL_LINK_TEXT, "Конструктор"),
        ]
        end_time = time.time() + timeout
        last_exception = None
        while time.time() < end_time:
            for by, locator in constructor_locators:
                try:
                    btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((by, locator))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    try:
                        btn.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", btn)
                    return self
                except Exception as e:
                    last_exception = e
                    continue
            time.sleep(0.2)
        raise RuntimeError(f"Go to constructor button not found after {timeout}s. Last exception: {last_exception}")
    

    def _move_to(self, bun_locator, destination_locator, timeout: int = 15) -> bool:
        t = self.timeout if timeout is None else timeout
        try:
            bun = WebDriverWait(self.driver, t).until(
                EC.presence_of_element_located(bun_locator)
            )
            destination = WebDriverWait(self.driver, t).until(
                EC.presence_of_element_located(destination_locator)
            )
        except Exception:
            return False
        try:
            self.driver.execute_script(bun, destination)
            if self._element_is_descendant(destination, bun):
                return True
        except Exception:
            pass
        try:
            actions = ActionChains(self.driver)
            actions.drag_and_drop(bun, destination).perform()
            if self._element_is_descendant(destination, bun):
                return True
        except Exception:
            pass
        return False


    def move_bun_to_add_block_and_verify_number(self, timeout = 10) -> bool:
        try:
            self.wait_invisible(base_page_locators.OVERLAY, timeout)
        except Exception:
            self.wait_invisible(("css selector", "div.Modal_modal_overlay"), timeout)
            self.wait_invisible((By.XPATH, "//div[contains(@class,'Modal_modal_overlay__x2ZCr')]"), timeout)
        self.wait_invisible(base_page_locators.OVERLAY, timeout)
        self.wait_visible(base_page_locators.BUN_NUMBER_EMPTY)
        self.drag_and_drop(base_page_locators.BUN, base_page_locators.INGREDIENT_BLOCK, timeout)
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(base_page_locators.BUN_NUMBER_FILLED)
        )
        text = (el.text or "").strip()
        try:
            value = int(text)
        except ValueError:
            return False
        return value == 2


    def drag_and_drop_js(self, source, target) -> None:
        self.wait_visible(source)
        self.wait_visible(target)
        src_el = self.find(source)
        tgt_el = self.find(target)
        self.scroll_into_view(src_el)
        self.scroll_into_view(tgt_el)
        self.driver.execute_script(
            """
            var s = arguments[0], t = arguments[1];
            function fire(el, type, dt){
            var e = document.createEvent('CustomEvent');
            e.initCustomEvent(type, true, true, null);
            e.dataTransfer = dt;
            el.dispatchEvent(e);
            }
            var dt = {data:{}, setData(k,v){this.data[k]=v}, getData(k){return this.data[k]}};
            fire(s,'dragstart',dt); fire(t,'dragenter',dt); fire(t,'dragover',dt); fire(t,'drop',dt); fire(s,'dragend',dt);
            """,
            src_el, tgt_el,
        )


    def add_ingredient_by_drag(self, name: str):
        source = self.find((By.XPATH, f"//span[text()='{name}']/ancestor::button"))
        target = self.find(base_page_locators.INGREDIENT_BLOCK)
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(self.driver).drag_and_drop(source, target).perform()



    def build_burger_with_drag_and_drop(self, timeout=45) -> None:
        self.scroll_to_top()
        overlay_locator = ("css selector", "div.Modal_modal_overlay__x2ZCr")
        try:
            self.wait_invisible(overlay_locator, timeout)
        except Exception:
            self.wait_invisible(("css selector", "div.Modal_modal_overlay"), timeout)
        self.wait_visible(base_page_locators.BUNS_SECTION, timeout)
        self.click(base_page_locators.BUNS_SECTION)
        try:
            self.wait_invisible(base_page_locators.OVERLAY, timeout)
        except Exception:
            self.wait_invisible(("css selector", "div.Modal_modal_overlay"), timeout)
            self.wait_invisible((By.XPATH, "//div[contains(@class,'Modal_modal_overlay__x2ZCr')]"), timeout)
        self.wait_invisible(base_page_locators.OVERLAY, timeout)
        self.drag_and_drop(base_page_locators.BUN, base_page_locators.INGREDIENT_BLOCK, timeout)
        self.drag_and_drop(base_page_locators.BUN_2, base_page_locators.INGREDIENT_BLOCK, timeout)
        self.wait_invisible(base_page_locators.OVERLAY, timeout=15)
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(base_page_locators.SAUCES_SECTION,)).click()
        self.wait_invisible(base_page_locators.OVERLAY, timeout=15)
        self.drag_and_drop(base_page_locators.SAUCE, base_page_locators.INGREDIENT_BLOCK, timeout)
        self.drag_and_drop(base_page_locators.SAUCE_2, base_page_locators.INGREDIENT_BLOCK, timeout)
        return


    def drag_and_drop(self, source_locator, target_locator, timeout=10):
        source = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(source_locator))
        target = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(target_locator))
        actions = ActionChains(self.driver)
        try:
            actions.drag_and_drop(source, target).perform()
        except Exception:
            actions.click_and_hold(source).pause(0.2).move_to_element(target).release().perform()


    def try_get_order_number_from_modal(self, timeout=105) -> Optional[str]:
        if not self.is_visible(base_page_locators.MODAL_ORDER_NUMBER, timeout):
            return None
        num = (self.find(base_page_locators.MODAL_ORDER_NUMBER).text or "").strip()
        if num and not num.startswith("#"):
            num = f"#0{num}"
        return num or None







    @allure.step("Попытаться оформить заказ, если кнопка активна")
    def place_order_if_enabled(self) -> bool:
        self.close_overlays_if_any()
        self.wait_gone(base_page_locators.OVERLAY)

        try:
            btn = self.wait_clickable(base_page_locators.ORDER_BUTTON)
        except TimeoutException:
            # Кнопка недоступна в течение заданного времени
            return False

        text = (btn.text or "").strip().lower()

        if "войти" in text:
            return False

        try:
            btn.click()
            time.sleep(15)  # задержка после клика, чтобы окно/модалка успели появиться
            return True
        except ElementClickInterceptedException:
            self.close_overlays_if_any()
            self.wait_gone(base_page_locators.OVERLAY)
            self.js_click(btn)
            return True
        except TimeoutException:
            # Если повторно не получилось кликнуть
            return False
        except Exception:
            # Любая непредвиденная ошибка, безопасно возвращаем False
            return False