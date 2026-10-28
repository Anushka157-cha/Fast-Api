from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Task Manager API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./tasks.db",
        description="Database connection URL (SQLite for local dev, PostgreSQL for production)"
    )

    # JWT Authentication & Security
    JWT_SECRET_KEY: str = Field(
        default="insecure-dev-secret-key-change-in-production-min32chars",
        description="Secret key used for signing JWT access tokens"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cross-Origin Resource Sharing (CORS)
    ALLOWED_ORIGINS: Union[List[str], str] = Field(
        default=[
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "*"
        ],
        description="List of origins allowed to make cross-origin requests"
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
