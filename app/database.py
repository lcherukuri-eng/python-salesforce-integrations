import os
import psycopg
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = (
    f"host={POSTGRES_HOST} "
    f"port={POSTGRES_PORT} "
    f"dbname={os.getenv('POSTGRES_DB')} "
    f"user={os.getenv('POSTGRES_USER')} "
    f"password={os.getenv('POSTGRES_PASSWORD')}"
)

def get_connection():
    return psycopg.connect(DATABASE_URL)

async_pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5,
    open=False,
)