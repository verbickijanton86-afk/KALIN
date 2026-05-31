from aiogram import Router, Bot, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import config
import database as db

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer("👋 Привет, Админ! Отправь мне текст, чтобы опубликовать его в канал.")
        return

    await message.answer(
        "👋 Привет! Я инструмент для анонимных сообщений.\n\n"
        "✍️ **Просто напиши мне любой текст**, и я передам его администратору анонимно!"
    )


@user_router.message(F.text)
async def handle_user_message(message: Message, bot: Bot):
    # Если пишет админ, этот хэндлер его игнорирует (для него есть admin.py)
    if message.from_user.id == config.ADMIN_ID:
        return

    # Отправляем сообщение админу
    admin_msg_text = f"📩 **Получено анонимное сообщение:**\n\n\"{message.text}\""

    # Кнопка для деанонимизации через оплату звездами
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕵️‍♂️ Узнать автора (⭐️ 10)", callback_data=f"pay_{message.message_id}")]
    ])

    try:
        # Пересылаем сообщение админу
        sent_msg = await bot.send_message(chat_id=config.ADMIN_ID, text=admin_msg_text, reply_markup=kb,
                                          parse_mode="Markdown")

        # Сохраняем реальные данные автора в базу данных, привязывая к ID сообщения у админа
        await db.save_message(
            msg_id=sent_msg.message_id,
            user_id=message.from_user.id,
            username=message.from_user.username or "нет юзернейма",
            full_name=message.from_user.full_name
        )

        await message.answer("🚀 Ваше сообщение успешно и анонимно передано администратору!")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при отправке сообщения админу. Попробуйте позже.")
        print(f"Ошибка отправки админу: {e}")
