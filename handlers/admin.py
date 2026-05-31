from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID, CHANNEL_ID
from database import db

admin_router = Router()


class AdminStates(StatesGroup):
    writing_post = State()


@admin_router.message(Command("admin"))
async def admin_start(message: types.Message):
    """Админ панель"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ты не админ")
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📝 Написать пост в канал", callback_data="write_post")],
    ])

    await message.answer(
        f"👨‍💼 Админ панель\n\n"
        f"Канал ID: {CHANNEL_ID}\n\n"
        f"Выбери действие:",
        reply_markup=keyboard
    )


@admin_router.callback_query(F.data == "write_post")
async def write_post_callback(callback: types.CallbackQuery, state: FSMContext):
    """Начало процесса написания поста"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ты не админ", show_alert=True)
        return

    await state.set_state(AdminStates.writing_post)
    await callback.message.answer(
        "📝 Отправь текст для поста в канал:\n\n(Используй <b>HTML теги</b> для форматирования)")
    await callback.answer()


@admin_router.message(AdminStates.writing_post)
async def admin_post_text(message: types.Message, state: FSMContext):
    """Получение текста поста"""
    if message.from_user.id != ADMIN_ID:
        return

    if not message.text:
        await message.answer("❌ Отправь текстовое сообщение")
        return

    # Сохраняем текст в state
    await state.update_data(post_text=message.text)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish_post")],
        [types.InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_post")],
    ])

    await message.answer(
        f"<b>Предпросмотр:</b>\n\n{message.text}\n\n"
        f"Опубликовать в канал?",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@admin_router.callback_query(F.data == "publish_post")
async def publish_post(callback: types.CallbackQuery, state: FSMContext):
    """Публикация поста в канал"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ты не админ", show_alert=True)
        return

    data = await state.get_data()
    text = data.get("post_text")

    if not text:
        await callback.answer("❌ Текст поста не найден", show_alert=True)
        return

    try:
        await callback.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode="HTML"
        )
        await callback.message.edit_text("✅ Пост опубликован в канал!")
        await state.clear()
        await callback.answer()
    except Exception as e:
        error_msg = str(e)
        await callback.message.edit_text(
            f"❌ Ошибка при публикации:\n\n"
            f"<code>{error_msg}</code>\n\n"
            f"💡 Проверь CHANNEL_ID в .env файле",
            parse_mode="HTML"
        )
        print(f"PUBLISH ERROR: {e}")
        await callback.answer()


@admin_router.callback_query(F.data == "cancel_post")
async def cancel_post(callback: types.CallbackQuery, state: FSMContext):
    """Отмена публикации"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ты не админ", show_alert=True)
        return

    await callback.message.edit_text("❌ Публикация отменена")
    await state.clear()
    await callback.answer()
