from fastapi import APIRouter
from sqlmodel import select
from app.api.deps import SessionDep

from app.api.endpoints import login, users, pets, searches
from app.models import Search, SearchReadWAll

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(pets.router, prefix="/users/{user_id}/pets", tags=["pets"])
api_router.include_router(
    searches.router, prefix="/users/{user_id}/searches", tags=["searches"]
)


@api_router.get(
    "/feed",
    response_model=list[SearchReadWAll],
)
async def feed(session: SessionDep, skip: int = 0, limit: int = 10):
    statement = select(Search).offset(skip).limit(limit)
    searches = session.exec(statement).all()
    return searches
