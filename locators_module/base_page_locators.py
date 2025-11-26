from selenium.webdriver.common.by import By

# Селектор кнопки Конструктор
CONSTRUCTOR_TAB = (By.XPATH, "//p[contains(@class,'AppHeader_header__linkText__3q_va') and contains(@class,'ml-2') and normalize-space(.)='Конструктор']")

# Селектор текст-кнопки Лента заказов
ORDER_TAPE_TAB = (By.CSS_SELECTOR, "a.AppHeader_header__link__3D_hX[href='/feed']")

# Селектор для логотипа Stellar burgers
LOGO = (By.XPATH, "//svg[@xmlns='http://www.w3.org/2000/svg' and @width='290' and @height='50']")

# Селектор для кнопки Булки
BUNS_SECTION = (By.XPATH, "//div[contains(@class, 'tab_tab__1SPyG')]//span[text()='Булки']")

# Селектор для кнопки Соусы
SAUCES_SECTION = (By.XPATH, "//div[contains(@class, 'tab_tab__1SPyG')]//span[text()='Соусы']")

# Селектор для кнопки Начинки
FILLINGS_SECTION = (By.XPATH, "//div[contains(@class, 'tab_tab__1SPyG')]//span[text()='Начинки']")

# Селектор текста Конструктор на главной странице
CONSTRUCTOR_TEXT = (By.CLASS_NAME, "text_type_main-large")

# Селектор окна с деталями ингредиента
INGREDIENT_MODAL = (By.XPATH, "//div[contains(@class,'Modal_modal__contentBox__sCy8X') and contains(@class,'pt-10') and contains(@class,'pb-15')]//h2")

# Селектор оверлея окна с деталями ингедиента
MODAL_OVERLAY = (By.XPATH, "//div[contains(@class,'Modal_modal_overlay')]")

# Селектор закрытия окна с деталями ингредиента
INGREDIENT_MODAL_CLOSE = (By.XPATH, "//section[contains(@class,'Modal')]//button[contains(@class,'close') or @aria-label='Закрыть']")

# Селектор оверлея для окна с деталями ингредиента
OVERLAY = (By.XPATH, "//div[contains(@class,'Modal_modal_overlay__x2ZCr')]")

# Селектор номера заказа в окне заказ оформлен
ORDER_NUMBER = (By.XPATH, "//h2[contains(@class,'Modal_modal__title_shadow') or contains(@class,'Modal_modal__title')]")

# Селектор области конструктора
CONSTRUCTOR_AREA = (By.XPATH, "//section[contains(@class,'BurgerConstructor_basket__29Cd7') and contains(@class,'mt-25')]/ul")

# Селектор кнопки оформления заказа
ORDER_BUTTON = (By.XPATH, "//button[contains(@class,'button_button') and contains(@class,'button_button_type_primary') and contains(@class,'button_button_size_large') and normalize-space(.)='Оформить заказ']")

# Селектор для булочки
BUN = (By.XPATH, "//img[@alt='Краторная булка N-200i' and contains(@class, 'BurgerIngredient_ingredient__image')]")

# Селектор для булочки, дублер
BUN_2 = (By.XPATH, "//a[contains(@class, 'BurgerIngredient_ingredient__1TVf6') and @href='/ingredient/61c0c5a71d1f82001bdaaa6c' and @draggable='true' and .//img[@alt='Краторная булка N-200i']]")

# Селектор для соуса
SAUCE = (By.CSS_SELECTOR, "img[class*='BurgerIngredient_ingredient__image'][alt='Соус Spicy-X']")

# Селектор для соуса, дублер
SAUCE_2 = (By.XPATH, "//a[contains(@class,'BurgerIngredient_ingredient__1TVf6') and @href='/ingredient/61c0c5a71d1f82001bdaaa72' and .//p[contains(@class,'BurgerIngredient_ingredient__text') and normalize-space(.)='Соус Spicy-X']]")

# Селектор для котлеты 
FILLING = (By.XPATH, "//div[contains(@class,'BurgerIngredient_ingredient')]//img[contains(@class,'BurgerIngredient_ingredient__image') and @alt='Мясо бессмертных моллюсков Protostomia']")

#Селектор для котлеты, дублер
FILLING_2 = (By.XPATH, "//a[contains(@class, 'BurgerIngredient_ingredient__1TVf6') and @href='/ingredient/61c0c5a71d1f82001bdaaa70' and .//img[@alt='Говяжий метеорит (отбивная)']]")

# Селектор невыбранного ингредиента
BUN_NUMBER_EMPTY = (By.XPATH, "//p[normalize-space(.)='0']")

# Селектор счетчика ингредиента который был добавлен
BUN_NUMBER_FILLED = (By.XPATH, "//p[normalize-space(.)='2']")

# Селектор блока с добавлением ингридиентов
INGREDIENT_BLOCK = (By.CSS_SELECTOR, "ul[class*='BurgerConstructor_basket__list']")

# Селектор номера заказа в окне заказа
MODAL_ORDER_NUMBER = (By.CSS_SELECTOR, "h2.Modal_modal__title__2L34m.Modal_modal__title_shadow__3ikwq")