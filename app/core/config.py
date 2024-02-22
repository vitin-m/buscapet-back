import secrets
from typing import Annotated
from pathlib import Path

from pydantic import (
    BeforeValidator,
    PostgresDsn,
    AnyHttpUrl,
    AfterValidator,
    ValidationInfo,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def db_uri_validator(v: str, info: ValidationInfo):
    if isinstance(v, str) and v:
        return v
    values = info.data
    uri = PostgresDsn.build(  # type: ignore
        scheme="postgresql+psycopg",
        username=values.get("POSTGRES_USER"),
        password=values.get("POSTGRES_PASSWORD"),
        host=values.get("POSTGRES_HOST"),
        port=values.get("POSTGRES_PORT"),
        path=f"{values.get('POSTGRES_DB') or ''}",
    )
    return str(uri)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str

    STATIC_PATH: Path = Path().absolute().joinpath("static")

    API_PATH: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3

    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    SQLALCHEMY_DATABASE_URI: Annotated[str, AfterValidator(db_uri_validator)] = ""

    SUPERUSER_USERNAME: str
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str


settings = Settings()  # type: ignore
