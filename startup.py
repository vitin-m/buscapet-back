import logging

from sqlmodel import Session, select
from dotenv import find_dotenv, load_dotenv
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.db import init_db
from app.db.engine import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def wait_for_db_startup() -> None:
    try:
        with Session(engine) as session:
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def main():
    logger.info("Initializing database...")
    dotenv_status = load_dotenv(find_dotenv())
    logger.info(f".env load status: {'sucess' if dotenv_status else 'failiure'}")
    wait_for_db_startup()
    with Session(engine) as session:
        init_db(session, logger)
    logger.info("Database initialized")

    # Path().absolute().joinpath("static").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
