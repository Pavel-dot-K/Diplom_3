from urllib.parse import urljoin

class Urls:

    BASE_URL = "https://stellarburgers.education-services.ru/"

    ORDER_PAGE = urljoin(BASE_URL, "feed") # Добавлена конкатенация по комментарию №4