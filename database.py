import aiosqlite
from config import DB_PATH
from datetime import datetime


class Database:
    def __init__(self):
        self.db_path = DB_PATH

    async def init(self):
        """Инициализация БД при запуске бота"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица анонимных сообщений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_id INTEGER,
                    channel_message_id INTEGER
                )
            """)

            # Таблица платежей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES messages(id)
                )
            """)

            await db.commit()

    async def save_message(self, user_id: int, message_text: str) -> int:
        """Сохранение анонимного сообщения"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages (user_id, message_text) VALUES (?, ?)",
                (user_id, message_text)
            )
            await db.commit()

            # Возвращаем ID добавленного сообщения
            cursor = await db.execute("SELECT last_insert_rowid()")
            result = await cursor.fetchone()
            return result[0]

    async def update_message_ids(self, message_id: int, channel_message_id: int):
        """Обновление ID сообщений"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE messages SET channel_message_id = ? WHERE id = ?",
                (channel_message_id, message_id)
            )
            await db.commit()

    async def get_message_sender(self, message_id: int) -> int | None:
        """Получение ID отправителя по ID сообщения"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM messages WHERE id = ?",
                (message_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else None

    async def save_payment(self, user_id: int, message_id: int, amount: int):
        """Сохранение платежа"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO payments (user_id, message_id, amount) VALUES (?, ?, ?)",
                (user_id, message_id, amount)
            )
            await db.commit()

    async def get_user_payments(self, user_id: int, message_id: int) -> list:
        """Проверка, платил ли пользователь за это сообщение"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM payments WHERE user_id = ? AND message_id = ?",
                (user_id, message_id)
            )
            return await cursor.fetchall()


db = Database()
