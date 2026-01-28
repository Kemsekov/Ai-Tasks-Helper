from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str

    # Backend settings
    backend_container_name: str
    backend_internal_host: str
    backend_internal_port: int
    backend_port: int
    backend_secret: str
    backend_debug: bool = False

    # AI settings
    openrouter_token: str
    default_model: str = "qwen/qwen3-coder:free"

    @property
    def database_url(self):
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"

settings = Settings()