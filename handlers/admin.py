from aiogram import Router, F
from aiogram.types import CallbackQuery
from config import ADMIN_ID
from database import ban_user

admin_router = Router()


@admin_router.callback_query(F.data.startswith("reveal_"))
async def process_reveal(callback: CallbackQuery):
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.answer("❌ У вас нет прав!", show_alert=True)
        return

    target_id = int(callback.data.split("_")[1])

    try:
        user_info = await callback.bot.get_chat(chat_id=target_id)
        mention = user_info.mention_html(user_info.full_name or "Пользователь")
        username = f"@{user_info.username}" if user_info.username else "скрыт"

        text = (
            f"🔎 **Данные автора:**\n\n"
            f"👤 Имя: {mention}\n"
            f"🆔 ID: <code>{target_id}</code>\n"
            f"🔗 Юзернейм: {username}"
        )
        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()
    except Exception:
        await callback.answer("❌ Не удалось получить данные аккаунта.", show_alert=True)


@admin_router.callback_query(F.data.startswith("ban_"))
async def process_ban(callback: CallbackQuery):
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.answer("❌ У вас нет прав!", show_alert=True)
        return

    target_id = int(callback.data.split("_")[1])

    await ban_user(target_id)
    await callback.message.answer(f"🚫 Пользователь с ID <code>{target_id}</code> забанен.", parse_mode="HTML")
    await callback.answer("Пользователь забанен!")
    await callback.message.edit_reply_markup(reply_markup=None)
