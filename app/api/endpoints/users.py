from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.db import crud
from app.models import (
    Message,
    UserCreate,
    User,
    UserCreateOpen,
    UserRead,
    UserReadWSearchPet,
    UserUpdate,
)
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
    val_user_response,
)

router = APIRouter()


@router.post("/open", response_model=UserRead)
async def create_user_open(session: SessionDep, user_in: UserCreateOpen):
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, to_create=user_create)
    return user


@router.get("/me", response_model=UserReadWSearchPet)
async def read_user_me(current_user: CurrentUser):
    return current_user


@router.put("/me", response_model=UserReadWSearchPet)
async def update_user_me(
    session: SessionDep, user_in: UserUpdate, current_user: CurrentUser
):
    user = crud.update_user(session, current_user, user_in)
    return user


@router.get(
    "/{user_id}",
    dependencies=[Depends(get_current_user)],
    response_model=UserReadWSearchPet,
)
async def read_user_by_id(user_id: int, session: SessionDep):
    user = val_user_response(session.get)(User, user_id)  # type: ignore
    return user


@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    response_model=list[UserRead],
)
async def get_users(session: SessionDep, skip: int = 0, limit: int = 100):
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users


@router.post("/", dependencies=[Depends(get_current_active_superuser)])
async def create_user(*, session: SessionDep, to_create: UserCreate):
    user = crud.get_user_by_email(session=session, email=to_create.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = crud.create_user(session=session, to_create=to_create)
    return user


@router.put(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserRead,
)
async def update_user(
    *,
    session: SessionDep,
    user_id: int,
    user_in: UserUpdate,
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="No user with this username",
        )
    user = crud.update_user(session, user, user_in)
    return user


@router.delete("/{user_id}")
async def deactivate_user(
    session: SessionDep, current_user: CurrentUser, user_id: int
) -> Message:
    user = val_user_response(session.get)(User, user_id)  # type: ignore
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions"
        )
    if user == current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users are not allowed to delete themselves",
        )

    user.is_active = False

    session.add(user)
    session.commit()
    return Message(message="User deleted successfully")
