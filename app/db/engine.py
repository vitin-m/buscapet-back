from sqlmodel import create_engine
from pydantic_core import Url

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))  # type: ignore
