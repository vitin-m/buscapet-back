from fastapi import APIRouter
from sqlmodel import select

from app.db import crud
from app.models import (
    SearchUpdate,
    User,
    Pet,
    NewSearch,
    Search,
    SearchReadWAll,
)
from app.api.deps import (
    CurrentUser,
    SessionDep,
    val_pet_response,
    val_search_response,
    val_user_response,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[SearchReadWAll],
)
async def get_searches_by_user_id(
    user_id: int,
    current_user: CurrentUser,
    session: SessionDep,
    skip: int = 0,
    limit: int = 10,
):
    val_user_response(session.get, user_id)(User, current_user.id)  # type: ignore
    statement = (
        select(Search).where(Search.user_id == user_id).offset(skip).limit(limit)
    )
    searches = session.exec(statement).all()
    return searches


@router.post("/{pet_id}", response_model=SearchReadWAll)
async def create_search_by_pet_id(
    user_id: int,
    pet_id: int,
    current_user: CurrentUser,
    session: SessionDep,
    new_search: NewSearch,
):
    val_user_response(session.get, user_id)(User, current_user.id)  # type: ignore
    val_pet_response(session.get, user_id)(Pet, pet_id)  # type: ignore
    search = crud.create_search(session, new_search, user_id, pet_id)

    return search


@router.put("/{pet_id}/{search_id}", response_model=SearchReadWAll)
async def update_search_by_pet_id(
    user_id: int,
    pet_id: int,
    search_id: int,
    current_user: CurrentUser,
    session: SessionDep,
    update_search: SearchUpdate,
):
    val_user_response(session.get, user_id)(User, current_user.id)  # type: ignore
    val_pet_response(session.get)(Pet, pet_id)  # type: ignore
    search = val_search_response(session.get, pet_id)(Search, search_id)  # type: ignore

    search = crud.update_search(
        session,
        search,
        update_search,
    )
