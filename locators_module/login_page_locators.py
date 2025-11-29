from selenium.webdriver.common.by import By

# Селектор текст-кнопки Зарегистрироваться
REGISTER_LINK = (By.XPATH, ".//a[normalize-space(.)='Зарегистрироваться']")

# Селектор поля ввода Имя
NAME_INPUT = (By.XPATH, ".//label[normalize-space(text())='Имя']/following-sibling::input")

# Селектор поля ввода Логина
EMAIL_INPUT = (By.XPATH, ".//label[normalize-space(text())='Email']/following-sibling::input")

# Селектор поля ввода Пароля
PASSWORD_INPUT = (By.XPATH, ".//label[normalize-space(text())='Пароль']/following-sibling::input")

# Селектор для кнопки Зарегистрироваться
REGISTER_BUTTON = (By.CSS_SELECTOR, "form button[type='submit'], button[data-testid='register'], button.btn-register")

# Селектор кнопки Войти
ENTER_BUTTON = (By.XPATH, ".//button[normalize-space(.)='Войти']")