import aiosqlite

DB_PATH = "bot.db"

async def init_db():
    """Создает таблицу для связи анонимных сообщений с их авторами"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msg_id INTEGER UNIQUE,
                user_id INTEGER,
                username TEXT,
                full_name TEXT
            )
        """)
        await db.commit()

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()

async def save_message(msg_id: int, user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO messages (msg_id, user_id, username, full_name) VALUES (?, ?, ?, ?)",
            (msg_id, user_id, username, full_name)
        )
        await db.commit()

async def get_author(msg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id, username, full_name FROM messages WHERE msg_id = ?", (msg_id,)) as cursor:
            return await cursor.fetchone()

async def create_ban_table():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS banned_users (
                user_id INTEGER PRIMARY KEY,
                ban_reason TEXT,
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()

async def is_user_banned(user_id: int) -> bool:
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute("SELECT 1 FROM banned_users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone() is not None

# Функция для добавления пользователя в бан (для админа)
async def ban_user(user_id: int, reason: str = "Нарушение правил"):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO banned_users (user_id, ban_reason) VALUES (?, ?)",
            (user_id, reason)
        )
        await db.commit()

# Добавьте в самый конец файла database.py

async def get_user_from_db(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT username FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]  # Возвращает username (строку)
            return None

