from logging import Logger
from sqlmodel import Session, select

from app.core.config import settings
from app.models import SQLModel, User, UserCreate
from app.db import crud
from app.db.engine import engine


def init_db(session: Session, logger: Logger):
    # Create tables
    SQLModel.metadata.create_all(bind=engine)
    logger.info("Table created")

    user = session.exec(
        select(User).where(User.username == settings.SUPERUSER_USERNAME)
    ).first()

    if not user:
        superuser_in = UserCreate(
            username=settings.SUPERUSER_USERNAME,
            email=settings.SUPERUSER_EMAIL,
            password=settings.SUPERUSER_PASSWORD,
            is_superuser=True,
        )

        user = crud.create_user(session, superuser_in)
        logger.info("Superuser created")
