from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FastAPI Template"
    app_version: str = "1.0.0"

    db_host: str = "db"
    db_port: int = 5432
    postgres_db: str = "fastapi"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 240

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0


settings = Settings()
