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
