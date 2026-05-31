import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_ID, RECIPIENT_ID, CHANNEL_ID
from database import db
from handlers.admin import admin_router
from handlers.user import user_router
from handlers.payments import payments_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Инициализация при запуске бота"""
    await db.init()
    logger.info("✅ База данных инициализирована")
    logger.info(f"📌 Admin ID: {ADMIN_ID}")
    logger.info(f"📨 Recipient ID: {RECIPIENT_ID}")
    logger.info(f"📢 Channel ID: {CHANNEL_ID}")


async def on_shutdown(bot: Bot):
    """Завершение при остановке бота"""
    logger.info("❌ Бот остановлен")


async def main():
    """Главная функция запуска бота"""

    # Проверяем конфиг
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен в .env!")
        return

    if not ADMIN_ID or not RECIPIENT_ID:
        logger.error("❌ ADMIN_ID или RECIPIENT_ID не установлены в .env!")
        return

    logger.info("🚀 Запуск бота...")

    # Инициализируем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры (порядок важен!)
    dp.include_router(payments_router)  # Платежи
    dp.include_router(admin_router)  # Админ команды
    dp.include_router(user_router)  # Обычные пользователи

    # Инициализируем БД
    try:
        await db.init()
        logger.info("✅ База данных готова")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        return

    # Удаляем старые вебхуки (если использовались раньше)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Вебхуки очищены")
    except Exception as e:
        logger.error(f"⚠️ Ошибка при удалении вебхуков: {e}")

    logger.info("📡 Бот начинает опрос сообщений...")
    logger.info("=" * 50)

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    except KeyboardInterrupt:
        logger.info("⏸️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.session.close()
        logger.info("✅ Сессия бота закрыта")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот завершён")
