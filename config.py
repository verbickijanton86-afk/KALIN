import os
from dotenv import load_dotenv

# Флаг override=True заставит Python принудительно стереть старый ID
# из памяти и взять новое значение из файла .env
load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Преобразуем в int и убираем возможные случайные пробелы
ADMIN_ID = int(os.getenv("ADMIN_ID").strip()) if os.getenv("ADMIN_ID") else None
CHANNEL_ID = int(os.getenv("CHANNEL_ID").strip()) if os.getenv("CHANNEL_ID") else None
