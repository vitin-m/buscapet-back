import secrets
from typing import Optional
from pathlib import Path

from pydantic import PostgresDsn, AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    SERVER: str
    USER: str
    PASSWORD: str
    DB: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", extra="ignore"
    )

    PROJECT_NAME: str

    STATIC_PATH: Path = Path().absolute().joinpath("static")

    API_PATH: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3

    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl

    POSTGRES: PostgresSettings
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")  # type: ignore
    @classmethod
    def assemble_db_uri(cls, v: Optional[str], values: ValidationInfo):
        if isinstance(v, str):
            return v
        postgres_cfg: PostgresSettings = values.data.get("POSTGRES")  # type: ignore
        return PostgresDsn.build(  # type: ignore
            scheme="postgresql",
            username=postgres_cfg.USER,
            password=postgres_cfg.PASSWORD,
            host=postgres_cfg.SERVER,
            path=f"{postgres_cfg.DB or ''}",
        )


settings = Settings()  # type: ignore
