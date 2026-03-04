import asyncpg
from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST
    )

async def close_db():
    await pool.close()