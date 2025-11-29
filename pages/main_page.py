from __future__ import annotations
from contextlib import suppress
import time
from typing import Tuple, Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from locators_module import base_page_locators
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
from pages.base_page import BasePage
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, MoveTargetOutOfBoundsException

Locator = Tuple[By, str]
MaybeEl = Union[Locator, WebElement, str]


class MainPage(BasePage):  


    def __init__(self, driver, timeout=15):
        with allure.step(f"Инициализация: timeout={timeout}"):
            super().__init__(driver, timeout)


    def close_ingredient_modal(self) -> None:
        with allure.step("Закрыть ингредиент-модальное окно"):
            self.close_overlays_if_any()


    def __init__(self, driver, timeout=15):
        with allure.step(f"Инициализация: timeout={timeout} (вторая версия)"):
            self.driver = driver
            self._default_timeout = timeout
            self.wait = WebDriverWait(driver, timeout)


    def _click_first_available(self, locators, timeout: int = 10) -> bool:
        with allure.step(f"Click first available: locators_count={len(locators)}, timeout={timeout}"):
                btn = EC.element_to_be_clickable((by, locator))
                btn.click()
                return True


    def click_bun(self, timeout=10) -> bool:
        with allure.step(f"Клик по булке (bun): timeout={timeout}"):
            self.click(base_page_locators.BUN)
            return True
    

    @property
    def modal_overlay_present(self) -> bool:
        with allure.step("Modal overlay presence check"):
            overlays = self.driver.find_elements(*base_page_locators.MODAL_OVERLAY)
            return bool(overlays)


    def is_ingredient_modal_displayed(self) -> bool:
        with allure.step("Проверяем наличие окна игредиента"):
            els = self.driver.find_elements(*base_page_locators.INGREDIENT_MODAL)
            return bool(els) and els[0].is_displayed()


    def is_ingredient_modal_absent(self, timeout: int = 5) -> bool:
        with allure.step("Проверяем отсутствие окна игредиента"):
            return self.is_visible(base_page_locators.INGREDIENT_MODAL)


    def close_overlays_if_any(self) -> None:
        with allure.step("Close overlays if any"):
            if self.modal_overlay_present:
                with allure.step("Если есть оверлей ингредиента, попытаться закрыть его"):
                    btns = self.finds(base_page_locators.INGREDIENT_MODAL_CLOSE)
                    if btns:
                        self.js_click(btns[0])
                with allure.step("Ожидание исчезновения ингредиент-модального окна (до 5 секунд)"):
                    end_time = time.time() + 5
                    while time.time() < end_time:
                        self.finds(base_page_locators.INGREDIENT_MODAL)
                        break
                return
            with allure.step("Проверка отсутствия ингредиент-модального окна в течение 15 секунд"):
                self.is_ingredient_modal_absent(timeout=15)


    # Исправлено по комментарию №11
    @allure.step("Переходим в'Ленту заказов'") 
    def go_to_feed(self) -> "MainPage":
        self.scroll_to_top()
        self.click(base_page_locators.ORDER_TAPE_TAB)
        return self


    @allure.step("Переходим в 'Конструктор'")
    def go_to_constructor(self) -> "MainPage":
        self.scroll_to_top()
        self.click(base_page_locators.CONSTRUCTOR_TAB)
        return self


    def _move_to(self, bun_locator, destination_locator, timeout: int = 15) -> bool:
        with allure.step(f"Move bun to destination: bun_locator={bun_locator}, destination_locator={destination_locator}, timeout={timeout}"):
            destination = base_page_locators.CONSTRUCTOR_AREA
            bun = base_page_locators.BUN
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
        with allure.step(f"Move bun to add block and verify number (timeout={timeout})"):        
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
        with allure.step("drag_and_drop_js: выполнить drag-and-drop через JS"):
            with allure.step("Ожидание видимости источника и цели"):
                self.wait_visible(source)
                self.wait_visible(target)
            with allure.step("Получение элементов источника и цели"):
                src_el = self.find(source)
                tgt_el = self.find(target)
            with allure.step("Прокрутить элементы в видимую область"):
                self.scroll_into_view(src_el)
                self.scroll_into_view(tgt_el)
            with allure.step("Выполнить JS-драг-дроп"):
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
        with allure.step(f"add_ingredient_by_drag: name={name}"):
            source = self.find((By.XPATH, f"//span[text()='{name}']/ancestor::button"))
            target = self.find(base_page_locators.INGREDIENT_BLOCK)
            with allure.step("Выполнить drag-and-drop через ActionChains"):
                ActionChains(self.driver).drag_and_drop(source, target).perform()


    def build_burger_with_drag_and_drop(self, timeout=45) -> None:
        with allure.step("build_burger_with_drag_and_drop: постройка бургера через drag-and-drop"):
            self.scroll_to_top()
            overlay_locator = ("css selector", "div.Modal_modal_overlay__x2ZCr")
            try:
                with allure.step("Ожидание исчезновения оверлея"):
                    self.wait_invisible(overlay_locator, timeout)
            except Exception:
                with allure.step("Ожидание исчезновения второго оверлея"):
                    self.wait_invisible(("css selector", "div.Modal_modal_overlay"), timeout)
            with allure.step("Ожидание видимости секции булок и выбор секции"):
                self.wait_visible(base_page_locators.BUNS_SECTION, timeout)
                self.click(base_page_locators.BUNS_SECTION)
            try:
                with allure.step("Ожидание исчезновения оверлея перед выбором соусов"):
                    self.wait_invisible(base_page_locators.OVERLAY, timeout)
            except Exception:
                with allure.step("Ожидание исчезновения модального оверлея перед соусами"):
                    self.wait_invisible(("css selector", "div.Modal_modal_overlay"), timeout)
                    self.wait_invisible((By.XPATH, "//div[contains(@class,'Modal_modal_overlay__x2ZCr')]"), timeout)
            with allure.step("Ожидание исчезновения основного оверлея"):
                self.wait_invisible(base_page_locators.OVERLAY, timeout)
            with allure.step("Перетаскивание булок в ингредиент-блок"):
                self.drag_and_drop(base_page_locators.BUN, base_page_locators.INGREDIENT_BLOCK, timeout)
                self.drag_and_drop(base_page_locators.BUN_2, base_page_locators.INGREDIENT_BLOCK, timeout)
            with allure.step("Ожидание исчезновения оверлея и выбор соусов"):
                self.wait_invisible(base_page_locators.OVERLAY, timeout=15)
                WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(base_page_locators.SAUCES_SECTION,)).click()
            with allure.step("Ожидание исчезновения оверлея перед соусами"):
                self.wait_invisible(base_page_locators.OVERLAY, timeout=15)
            with allure.step("Перетаскивание соусов в ингредиент-блок"):
                self.drag_and_drop(base_page_locators.SAUCE, base_page_locators.INGREDIENT_BLOCK, timeout)
                self.drag_and_drop(base_page_locators.SAUCE_2, base_page_locators.INGREDIENT_BLOCK, timeout)
            return


    def drag_and_drop(self, source_locator, target_locator, timeout=10):
        with allure.step(f"drag_and_drop: source={source_locator}, target={target_locator}, timeout={timeout}"):
            source = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(source_locator))
            target = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(target_locator))
            actions = ActionChains(self.driver)
            try:
                with allure.step("Выполнить обычное drag_and_drop через ActionChains"):
                    actions.drag_and_drop(source, target).perform()
            except Exception:
                with allure.step("Fallback: drag_and_drop через последовательность действий"):
                    actions.click_and_hold(source).pause(0.2).move_to_element(target).release().perform()


    def try_get_order_number_from_modal(self, timeout=105) -> Optional[str]:
        with allure.step(f"try_get_order_number_from_modal: timeout={timeout}"):
            if not self.is_visible(base_page_locators.MODAL_ORDER_NUMBER, timeout):
                with allure.step("Модальное окно заказа не видно за указанный тайм-аут"):
                    return None
            num = (self.find(base_page_locators.MODAL_ORDER_NUMBER).text or "").strip()
            if num and not num.startswith("#"):
                num = f"#0{num}"
            with allure.step("Возвращаем отформатированный номер заказа или None"):
                return num or None
            
            
    @allure.step("Попытаться оформить заказ, если кнопка активна")
    def place_order_if_enabled(self) -> bool:
        self.close_overlays_if_any()
        self.wait_gone(base_page_locators.OVERLAY)
        try:
            btn = self.wait_clickable(base_page_locators.ORDER_BUTTON)
        except TimeoutException:
            return False
        text = (btn.text or "").strip().lower()
        if "войти" in text:
            return False
        try:
            btn.click()
            time.sleep(15) 
            return True
        except ElementClickInterceptedException:
            self.close_overlays_if_any()
            self.wait_gone(base_page_locators.OVERLAY)
            self.js_click(btn)
            return True
        except TimeoutException:
            return False
        except Exception:
            return False