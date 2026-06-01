# middlewares/blacklist.py
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from database import is_user_banned  # Импортируем функцию проверки из вашей БД


class BlacklistMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        # Проверяем ID пользователя в базе данных
        if await is_user_banned(event.from_user.id):
            # Если пользователь забанен, просто игнорируем его сообщения
            # Можно отправить уведомление: await event.answer("Вы заблокированы в этом боте.")
            return

            # Если не забанен, пропускаем запрос дальше к хэндлерам
        return await handler(event, data)
