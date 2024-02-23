from typing import Union
from sqlmodel import Session, select

from app.models import (
    NewPet,
    NewSearch,
    NewSighting,
    Pet,
    Search,
    SearchUpdate,
    User,
    UserCreate,
    UserUpdate,
)
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
        to_create,
        update={
            "hashed_password": security.get_pwd_hash(to_create.password),
            "phone": str(to_create.phone),
            "image": str(to_create.image),
        },
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def update_user(session: Session, db_obj: User, obj_in: UserUpdate):
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


def create_pet(session: Session, to_create: NewPet, user_id: int):
    db_obj = Pet.model_validate(
        to_create, update={"user_id": user_id, "image": str(to_create.image)}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def create_sighting(session: Session, to_create: NewSighting, search_id: int):
    db_obj = Search.model_validate(to_create, update={"search_id": search_id})

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def create_search(session: Session, to_create: NewSearch, user_id: int, pet_id: int):
    db_obj = Search.model_validate(
        to_create, update={"user_id": user_id, "pet_id": pet_id}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    create_sighting(session, to_create.sighting, db_obj.id)  # type: ignore
    session.refresh(db_obj)
    return db_obj


def update_search(session: Session, db_obj: Search, obj_in: SearchUpdate):
    update_data = obj_in.model_dump(exclude_unset=True)

    for k, v in db_obj:
        setattr(db_obj, k, update_data.get(k, v))

    if obj_in.sighting:
        create_sighting(session, obj_in.sighting, db_obj.id)  # type: ignore

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj
