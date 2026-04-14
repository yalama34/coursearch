from urllib.parse import quote_plus

from src.settings import settings


def get_database_url() -> str:
    password = quote_plus(settings.DB_PASSWORD)

    return (
        f"postgresql+asyncpg://"
        f"{settings.DB_USER}:{password}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
