from fastapi import APIRouter, Depends, Form, HTTPException, status, File, UploadFile
from sqlmodel import select

from app.db import crud
from app.models import (
    Message,
    NewPet,
    Pet,
    PetRead,
    PetReadWSearch,
    Search,
    SearchReadWAll,
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
    save_image,
    val_pet_response,
    val_user_response,
)

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    response_model=list[SearchReadWAll],
)
async def get_searches(session: SessionDep, skip: int = 0, limit: int = 100):
    statement = select(Search).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users


@router.get("/", response_model=SearchReadWAll)
async def read_user_me(current_user: CurrentUser):
    return current_user


# @router.put("/me", response_model=UserRead)
# async def update_user_me(
#     *, session: SessionDep, user_in: UserUpdate, current_user: CurrentUser
# ):
#     user = crud.update_user(session, current_user, user_in)
#     return user


# @router.post("/me/pets", response_model=PetRead)
# async def add_pet(
#     session: SessionDep,
#     current_user: CurrentUser,
#     image: UploadFile = File(...),
#     new_pet: NewPet = Form(...),
# ):
#     image_link = await save_image(img=image, deco_str=new_pet.name)
#     pet = crud.create_pet(session, new_pet, current_user.id, str(image_link))  # type: ignore
#     return pet


# @router.delete("/me/pets/{pet_id}")
# async def remove_pet(
#     pet_id: int,
#     current_user: CurrentUser,
#     session: SessionDep,
# ):
#     pet = val_pet_response(session.get, current_user.id)(Pet, pet_id)  # type: ignore
#     session.delete(pet)
#     session.commit()

#     return Message(message="Pet deleted successfully")


# @router.get(
#     "/{user_id}",
#     dependencies=[Depends(get_current_user)],
#     response_model=UserReadWSearchPet,
# )
# async def read_user_by_id(user_id: int, session: SessionDep):
#     user = val_user_response(session.get)(User, user_id)  # type: ignore
#     return user


# @router.get(
#     "/{user_id}/pets",
#     dependencies=[Depends(get_current_user)],
#     response_model=list[UserRead],
# )
# async def read_user_pets(user_id: int, session: SessionDep):
#     user = val_user_response(session.get)(User, user_id)  # type: ignore
#     return user.pets


# @router.get(
#     "/{user_id}/pets/{pet_id}",
#     dependencies=[Depends(get_current_user)],
#     response_model=PetReadWSearch,
# )
# async def read_pet_by_id(user_id: int, session: SessionDep):
#     val_user_response(session.get)(User, user_id)  # type: ignore
#     pet = val_pet_response(session.get, user_id)(Pet, pet_id)  # type: ignore

#     return pet


# @router.get(
#     "/",
#     dependencies=[Depends(get_current_user)],
#     response_model=list[UserRead],
# )
# async def get_users(session: SessionDep, skip: int = 0, limit: int = 100):
#     statement = select(User).offset(skip).limit(limit)
#     users = session.exec(statement).all()
#     return users


# @router.post("/", dependencies=[Depends(get_current_active_superuser)])
# async def create_user(*, session: SessionDep, to_create: UserCreate):
#     user = crud.get_user_by_email(session=session, email=to_create.email)
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this username already exists in the system.",
#         )

#     user = crud.create_user(session=session, to_create=to_create)
#     return user


# @router.put(
#     "/{user_id}",
#     dependencies=[Depends(get_current_active_superuser)],
#     response_model=UserRead,
# )
# async def update_user(
#     *,
#     session: SessionDep,
#     user_id: int,
#     user_in: UserUpdate,
# ):
#     user = session.get(User, user_id)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="No user with this username",
#         )
#     user = crud.update_user(session, user, user_in)
#     return user


# @router.delete("/{user_id}")
# async def delete_user(
#     session: SessionDep, current_user: CurrentUser, user_id: int
# ) -> Message:
#     user = session.get(User, user_id)

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#         )
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions"
#         )
#     if user == current_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Users are not allowed to delete themselves",
#         )

#     user.is_active = False

#     session.add(user)
#     session.commit()
#     return Message(message="User deleted successfully")


# @router.delete("/{user_id}/pets/{pet_id}")
# async def delete_pet(
#     session: SessionDep, current_user: CurrentUser, user_id: int, pet_id: int
# ) -> Message:
#     user = val_user_response(session.get)(User, user_id)  # type: ignore
#     pet = val_pet_response(session.get, user.id)(Pet, pet_id)  # type: ignore

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#         )
#     if not pet:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found"
#         )

#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions"
#         )
#     if user.id != pet.user_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Pet does not belong to marked user",
#         )

#     session.delete(pet)
#     session.commit()
#     return Message(message="Pet deleted successfully")
