import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers.user import user_router
from handlers.admin import admin_router
from middlewares.blacklist import BlacklistMiddleware
from middlewares.subscription import SubscriptionMiddleware

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация проверок
    dp.message.middleware(BlacklistMiddleware())
    dp.message.middleware(SubscriptionMiddleware())

    # Подключение роутеров
    dp.include_router(user_router)
    dp.include_router(admin_router)

    print("Бот успешно запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
