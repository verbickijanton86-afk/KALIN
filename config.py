import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Получаешь от @BotFather

# ID администратора (твой ID)
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Узнаешь в @userinfobot

# ID пользователя, которому пересылаются анонимные сообщения
RECIPIENT_ID = int(os.getenv("RECIPIENT_ID"))

# ID канала для постов (начинается с -)
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Стоимость просмотра (в звёздах Telegram)
STAR_PRICE = 9  # 1 звезда = примерно $0.01, 9 звёзд = $0.099

# Путь к БД
DB_PATH = "bot.db"
