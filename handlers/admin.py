from aiogram import Router, F
from aiogram.types import CallbackQuery
from config import ADMIN_ID
from database import ban_user, get_user_from_db

admin_router = Router()


# 1. ОБРАБОТКА КНОПКИ РАСКРЫТИЯ АВТОРА
@admin_router.callback_query(F.data.startswith("reveal_"))
async def process_reveal(callback: CallbackQuery):
    # Проверка безопасности: только главный админ может нажимать кнопку
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.answer("❌ У вас нет прав для просмотра этой информации!", show_alert=True)
        return

    # Извлекаем ID пользователя из callback_data (все, что после "reveal_")
    target_id = int(callback.data.split("_")[1])

    # Запрашиваем имя пользователя из нашей локальной базы данных bot.db
    saved_username = await get_user_from_db(target_id)

    try:
        # Пробуем запросить свежие данные аккаунта через Telegram API
        user_info = await callback.bot.get_chat(chat_id=target_id)
        username = f"@{user_info.username}" if user_info.username else "скрыт"
        name = user_info.full_name or "Пользователь"
    except Exception:
        # Если API выдало ошибку (ограничения приватности), берем данные из бэкапа базы
        name = "Пользователь (данные из БД)"
        if saved_username:
            username = f"@{saved_username}"
        else:
            username = "скрыт в настройках"

    # Формируем красивую кликабельную ссылку на человека, если юзернейм открыт
    if username != "скрыт" and username != "скрыт в настройках":
        mention_text = f"<a href='t.me/{username.replace('@', '')}'>{name}</a>"
    else:
        mention_text = name

    text = (
        f"🔎 **Данные автора сообщения:**\n\n"
        f"👤 Имя: {mention_text}\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"🔗 Юзернейм: {username}\n\n"
        f"<i>(Вы можете скопировать ID для связи или забанить нарушителя кнопкой под сообщением)</i>"
    )

    # Отправляем админу карточку пользователя и убираем уведомление о загрузке кнопки
    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer("Данные успешно получены!")


# 2. ОБРАБОТКА КНОПКИ БАНА ПОЛЬЗОВАТЕЛЯ
@admin_router.callback_query(F.data.startswith("ban_"))
async def process_ban(callback: CallbackQuery):
    # Проверка безопасности
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.answer("❌ У вас нет прав!", show_alert=True)
        return

    # Извлекаем ID пользователя из callback_data (все, что после "ban_")
    target_id = int(callback.data.split("_")[1])

    # Добавляем ID в таблицу забаненных в SQLite
    await ban_user(target_id)

    # Отправляем текстовое подтверждение в чат админа
    await callback.message.answer(
        f"🚫 Пользователь с ID <code>{target_id}</code> успешно добавлен в черный список бота.",
        parse_mode="HTML"
    )
    await callback.answer("Пользователь забанен!")

    # Стираем инлайн-кнопки под сообщением, чтобы нельзя было нажать на них повторно
    await callback.message.edit_reply_markup(reply_markup=None)
