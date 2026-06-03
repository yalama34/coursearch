from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    STEPIK_CLIENT_ID: str
    STEPIK_CLIENT_SECRET: str
    ENABLED_PROVIDERS: str
    UDEMY_CLIENT_ID: str
    UDEMY_CLIENT_SECRET: str

    class Config:
        env_file = ".env"


settings = Settings()
