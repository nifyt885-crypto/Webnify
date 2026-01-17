import os

# Конфигурация бота
BOT_TOKEN = "8538212357:AAHWsvcYOsccLcI-m9C3XI1lPd19I1fszfE"
OWNER_ID = 8294608065

# Настройки базы данных
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'webnify'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', '')
}

# Платежная ссылка
PAYMENT_URL = "https://pay.cloudtips.ru/p/5fb41094"

# Цены на услуги
PRICES = {
    'site_easy': 49,
    'site_hard': 69,
    'bot': 99
}