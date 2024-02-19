from fastapi import APIRouter

from app.api.endpoints import login, static
from app.api.endpoints.users import users, pets, searches

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(pets.router, prefix="/{user_id}/pets", tags=["pets"])
api_router.include_router(
    searches.router, prefix="/{user_id}/searches", tags=["searches"]
)
# api_router.include_router(static.router, prefix="/cdn", tags=["users"])
