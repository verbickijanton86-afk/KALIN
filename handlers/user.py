from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from database import add_user

user_router = Router()

@user_router.message(F.text == "/start")
async def start_cmd(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("👋 Привет! Отправь мне любое сообщение, и я передам его админу анонимно.")

@user_router.message()
async def forward_anonymous_msg(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        await message.answer("Вы являетесь администратором бота.")
        return

    user_id = message.from_user.id

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔎 Узнать автора", callback_data=f"reveal_{user_id}"),
            InlineKeyboardButton(text="❌ Забанить", callback_data=f"ban_{user_id}")
        ]
    ])

    await message.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 **Новое анонимное сообщение:**\n\n{message.text}",
        reply_markup=admin_kb,
        parse_mode="Markdown"
    )
    await message.answer("🚀 Ваше сообщение успешно отправлено анонимно!")
