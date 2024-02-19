from typing import Union
from sqlmodel import Session, select

from app.models import NewPet, Pet, User, UserCreate, UserUpdate
from app.core import security


def get_user_by_email(session: Session, email: str) -> Union[User, None]:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(session: Session, email: str, password: str) -> Union[User, None]:
    user = get_user_by_email(session, email)
    if not user:
        return None
    if security.verify_pwd(password, user.hashed_password):
        return user
    return None


def create_user(session: Session, to_create: UserCreate) -> User:
    db_obj = User.model_validate(
        to_create, update={"hashed_password": security.get_pwd_hash(to_create.password)}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def update_user(session: Session, db_obj: User, obj_in: UserUpdate) -> User:
    update_data = obj_in.model_dump(exclude_unset=True)

    if plain_password := update_data.get("password"):
        hashed_password = security.get_pwd_hash(plain_password)
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    for k, v in db_obj:
        setattr(db_obj, k, update_data.get(k, v))

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def create_pet(session: Session, to_create: NewPet, user_id: int, image_file: str):
    db_obj = Pet.model_validate(
        to_create, update={"user_id": user_id, "image": image_file}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj
