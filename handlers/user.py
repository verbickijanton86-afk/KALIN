from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import RECIPIENT_ID, STAR_PRICE, ADMIN_ID
from database import db

user_router = Router()


class UserStates(StatesGroup):
    waiting_for_message = State()


@user_router.message(Command("start"))
async def user_start(message: types.Message):
    """Стартовое меню"""
    # Если админ - показываем админ-команды
    if message.from_user.id == ADMIN_ID:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✉️ Отправить сообщение", callback_data="send_message")],
            [types.InlineKeyboardButton(text="👨‍💼 Админ панель", callback_data="admin_panel")],
        ])
    else:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✉️ Отправить анонимное сообщение", callback_data="send_message")],
            [types.InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")],
        ])

    await message.answer(
        "👤 Привет! Это анонимный бот для сообщений.\n\n"
        "Здесь ты можешь:\n"
        "✉️ Отправить анонимное сообщение\n"
        "⭐ Посмотреть, кто писал (платно звёздами)",
        reply_markup=keyboard
    )


@user_router.callback_query(F.data == "send_message")
async def send_message_callback(callback: types.CallbackQuery, state: FSMContext):
    """Начало процесса отправки сообщения"""
    await state.set_state(UserStates.waiting_for_message)
    await callback.message.answer("✉️ Напиши своё анонимное сообщение:")
    await callback.answer()


@user_router.message(UserStates.waiting_for_message)
async def receive_user_message(message: types.Message, state: FSMContext):
    """Получение анонимного сообщения"""

    if not message.text:
        await message.answer("❌ Отправь текстовое сообщение")
        return

    try:
        # Сохраняем сообщение в БД
        message_id = await db.save_message(message.from_user.id, message.text)

        # Создаём кнопку для просмотра отправителя
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text=f"👤 Узнать автора (⭐{STAR_PRICE})",
                callback_data=f"show_sender_{message_id}"
            )],
        ])

        # Пересылаем получателю
        sent_message = await message.bot.send_message(
            chat_id=RECIPIENT_ID,
            text=f"📨 <b>Анонимное сообщение #{message_id}:</b>\n\n{message.text}",
            parse_mode="HTML",
            reply_markup=keyboard
        )

        # Сохраняем ID сообщения в БД
        await db.update_message_ids(message_id, sent_message.message_id)

        await message.answer(
            "✅ Твоё сообщение отправлено!\n"
            "Никто не узнает, что это писал(а) ты 🙂"
        )

    except Exception as e:
        await message.answer(
            f"❌ Ошибка при отправке:\n\n"
            f"<code>{str(e)}</code>\n\n"
            f"💡 Проверь RECIPIENT_ID в .env файле",
            parse_mode="HTML"
        )
        print(f"MESSAGE SEND ERROR: {e}")

    await state.clear()


@user_router.callback_query(F.data == "about")
async def about(callback: types.CallbackQuery):
    """Информация о боте"""
    await callback.message.edit_text(
        "ℹ️ <b>О боте</b>\n\n"
        "Это анонимный мессенджер для отправки сообщений.\n\n"
        "<b>Как это работает:</b>\n"
        "1️⃣ Ты отправляешь анонимное сообщение\n"
        "2️⃣ Оно попадает определённому пользователю\n"
        "3️⃣ Если нужно узнать автора - оплати звёздами\n\n"
        "<b>Конфиденциальность:</b>\n"
        "✅ Твой ID скрыт от других\n"
        "✅ Сообщения не отслеживаются",
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: types.CallbackQuery):
    """Переход в админ панель"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ты не админ", show_alert=True)
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📝 Написать пост в канал", callback_data="write_post")],
    ])

    await callback.message.edit_text(
        f"👨‍💼 Админ панель\n\n"
        f"Канал ID: {ADMIN_ID}\n\n"
        f"Выбери действие:",
        reply_markup=keyboard
    )
    await callback.answer()
