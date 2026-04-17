import os
from urllib.parse import quote_plus


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError("Database environment variables are not fully set")

DB_PASSWORD = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

REDIS_HOST = os.getenv("REDIS_HOST")
_redis_port = os.getenv("REDIS_PORT", "6379")
REDIS_PORT = int(_redis_port) if _redis_port.isdigit() else 6379

# Recommendation list cache TTL (seconds)
RECOMMENDATIONS_CACHE_TTL_SECONDS = int(os.getenv("RECOMMENDATIONS_CACHE_TTL_SECONDS", "3600"))

DATA_PATH = "data/raw/"
