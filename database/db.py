import os
import asyncpg
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

async def get_db_pool():
    if not DATABASE_URL:
        logger.error("SUPABASE_DATABASE_URL is not set.")
        raise ValueError("SUPABASE_DATABASE_URL is not set.")
    return await asyncpg.create_pool(DATABASE_URL)

async def init_db(pool):
    """Initialize database tables if they do not exist."""
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS costs (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                user_id BIGINT NOT NULL,
                username TEXT,
                category TEXT NOT NULL,
                amount NUMERIC NOT NULL,
                input_method TEXT NOT NULL,
                image_url TEXT
            )
        ''')
        logger.info("Database initialized successfully.")

async def insert_cost(pool, user_id: int, username: str, category: str, amount: float, input_method: str, image_url: str = None):
    """Insert a new cost record into the database."""
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO costs (user_id, username, category, amount, input_method, image_url)
            VALUES ($1, $2, $3, $4, $5, $6)
        ''', user_id, username, category, amount, input_method, image_url)
        logger.info(f"Cost recorded: {category} - {amount} by {username} ({input_method})")

async def get_total_cost(pool) -> float:
    """Get the aggregated total cost."""
    async with pool.acquire() as conn:
        val = await conn.fetchval('SELECT SUM(amount) FROM costs')
        return float(val) if val is not None else 0.0
