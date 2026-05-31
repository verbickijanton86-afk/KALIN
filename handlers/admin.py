from aiogram import Router, Bot, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
import config
import database as db  # Используем нашу базу для сохранения чистого текста

admin_router = Router()


# 1. ОБРАБОТЧИК КОМАНДЫ /START ДЛЯ АДМИНА
@admin_router.message(CommandStart(), F.from_user.id == config.ADMIN_ID)
async def admin_start(message: Message):
    await message.answer(
        "👋 Привет, Админ!\n\n"
        "📝 Напиши мне любой текст, и я предложу тебе опубликовать его в канал."
    )


# 2. ПРЕДПРОСМОТР ПОСТА И КНОПКИ УПРАВЛЕНИЯ
@admin_router.message(F.text, F.from_user.id == config.ADMIN_ID)
async def preview_admin_post(message: Message):
    # Защита от системных команд
    if message.text.startswith("/"):
        return

    text_to_post = message.text

    # Создаем инлайн-кнопки подтверждения и отмены.
    # В callback_data передаем ID сообщения админа, чтобы потом вытащить точный текст
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Опубликовать", callback_data=f"pub_{message.message_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")
        ]
    ])

    # Сохраняем чистый текст в базу данных (связываем с ID сообщения админа)
    # Используем существующую функцию или сохраняем под видом анонимного поста для простоты
    await db.save_message(
        msg_id=message.message_id,
        user_id=message.from_user.id,
        username=message.from_user.username or "admin",
        full_name=message.from_user.full_name
    )

    # Чтобы текст в базе точно обновился, если админ пишет повторно,
    # мы будем использовать текст самого сообщения message.text в хэндлере ниже.

    await message.answer(
        f"📋 **Предпросмотр поста:**\n\n{text_to_post}\n\n"
        f"Вы хотите опубликовать это в канал?",
        parse_mode="HTML",
        reply_markup=kb
    )


# 3. ДЕЙСТВИЕ ПРИ НАЖАТИИ «ОПУБЛИКОВАТЬ»
@admin_router.callback_query(F.data.startswith("pub_"))
async def confirm_publication(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    # Получаем ID оригинального сообщения, которое написал админ
    original_msg_id = int(callback.data.split("_")[1])

    try:
        # Пересылаем/копируем именно то чистое сообщение, которое прислал админ.
        # Метод copy_message отправляет только чистый текст/медиа без системного мусора бота!
        await bot.copy_message(
            chat_id=config.CHANNEL_ID,
            from_chat_id=callback.from_user.id,
            message_id=original_msg_id
        )

        # Меняем текст предпросмотра у админа на статус успеха
        await callback.message.edit_text("✅ Пост успешно опубликован в канале в чистом виде!")
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка публикации:\n`{e}`")

    await callback.answer()


# 4. ДЕЙСТВИЕ ПРИ НАЖАТИИ «ОТМЕНА»
@admin_router.callback_query(F.data == "cancel_post")
async def cancel_publication(callback: CallbackQuery):
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer()
        return

    await callback.message.edit_text("❌ Публикация отменена. Пост не отправлен.")
    await callback.answer("Отменено")
