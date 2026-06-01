# middlewares/subscription.py
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_ID  # Убедитесь, что CHANNEL_ID импортируется из вашего конфига


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        # Исключаем команду /start из проверки, чтобы пользователь мог запустить бота
        if event.text == "/start":
            return await handler(event, data)

        bot = data["bot"]
        try:
            # Запрашиваем статус пользователя в канале
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=event.from_user.id)

            # Разрешенные статусы: пользователь, администратор или создатель канала
            if member.status in ["member", "administrator", "creator"]:
                return await handler(event, data)

        except Exception:
            # Если возникла ошибка (например, бот не админ в канале), пропускаем пользователя во избежание сбоев
            return await handler(event, data)

        # Если подписки нет, отправляем сообщение с кнопкой-ссылкой на канал
        # Сначала получаем прямую ссылку на канал через бота
        chat = await bot.get_chat(CHANNEL_ID)
        invite_link = chat.invite_link or f"https://t.me{chat.username}"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться на канал", url=invite_link)]
        ])

        await event.answer(
            "⚠️ Для использования бота необходимо подписаться на наш официальный канал!",
            reply_markup=keyboard
        )
        return  # Прерываем выполнение, хэндлеры не сработают
