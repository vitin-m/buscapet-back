from sqlmodel import Session

from app.models import SQLModel

from .engine import engine


def init_db():
    SQLModel.metadata.create_all(bind=engine)
