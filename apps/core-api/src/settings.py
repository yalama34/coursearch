from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    REDIS_HOST = str
    REDIS_PORT = int

    ML_SERVICE_URL: str = "http://ml_service:8001"

    class Config:
        env_file = ".env"


settings = Settings()
