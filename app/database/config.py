from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 30
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_SOCKET_CONNECT_TIMEOUT: float = 1.0
    REDIS_SOCKET_TIMEOUT: float = 1.0
    REDIS_RETRIES: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
