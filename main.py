import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database as db
from handlers.user import user_router
from handlers.payments import payments_router
from handlers.admin import admin_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def main():
    # Инициализация базы данных
    await db.init_db()

    # Инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры в строгом порядке
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(payments_router)


    print("🤖 Бот успешно запущен и готов к работе!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
