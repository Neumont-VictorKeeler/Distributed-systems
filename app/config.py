from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./videogame_trading.db"
    secret_key: str = "your-secret-key-change-this-in-production-min-32-characters"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_notifications: str = "email-notifications"

    class Config:
        env_file = ".env"


settings = Settings()

