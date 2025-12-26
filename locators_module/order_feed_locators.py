from selenium.webdriver.common.by import By

# Селектор текста Лента заказов на странице Лента заказов
ORDER_TAPE_TEXT = (By.XPATH, "//h1[normalize-space(.)='Лента заказов']")

# Селектор для заказов в работе
HEADER_IN_PROGRESS = (By.XPATH, "//li[contains(@class,'text') and contains(@class,'text_type_digits-default') and contains(@class,'mb-2')]")

# Селектор для готовых заказов
HEADER_READY = (By.XPATH, "//li[contains(@class,'text') and contains(@class,'text_type_digits-default') and contains(@class,'mb-2')]")

# Селектор блока с номерами Готовых заказов
DONE_NUMBER_BLOCK = (By.XPATH, "//section[contains(@class,'order-feed')]//ul[contains(@class,'OrderFeed__done-list')]")

# Селектор блока с номерами заказов В работе
IN_WORK_NUMBER_BLOCK = (By.XPATH, "//section[contains(@class,'order-feed')]//ul[contains(@class,'OrderFeed__in-work')]")

# Селектор номера в разделе За все время
TOTAL_ALL_TIME = ( By.XPATH, "//p[normalize-space()='Выполнено за все время:']/following-sibling::p[contains(@class,'text_type_digits') and contains(@class,'OrderFeed_number')]" )

# Селектор номера в разделе Сегодня
TOTAL_TODAY = ( By.XPATH, "//p[normalize-space()='Выполнено за сегодня:']/following-sibling::p[contains(@class,'text_type_digits') and contains(@class,'OrderFeed_number')]" )

# Селектор номера ленты заказов
ORDER_TAPE_NUMBER = (By.XPATH, "//p[contains(@class,'text') and contains(@class,'text_type_digits-default') and contains(@class,'OrderFeed_number')]")