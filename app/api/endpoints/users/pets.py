from fastapi import APIRouter, Depends, Form, HTTPException, status, File, UploadFile

from app.db import crud
from app.models import (
    Message,
    NewPet,
    Pet,
    PetRead,
    PetReadWSearch,
    User,
    UserRead,
)
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_user,
    save_image,
    val_pet_response,
    val_user_response,
)

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    response_model=list[UserRead],
)
async def read_user_pets(user_id: int, session: SessionDep):
    user = val_user_response(session.get)(User, user_id)  # type: ignore
    return user.pets


@router.post("/", response_model=PetRead)
async def add_pet(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    image: UploadFile = File(...),
    new_pet: NewPet = Form(...),
):
    val_user_response(session.get, current_user.id)(User, user_id)  # type: ignore

    image_link = await save_image(img=image, deco_str=new_pet.name)
    pet = crud.create_pet(session, new_pet, user_id, str(image_link))  # type: ignore
    return pet


@router.get(
    "/{pet_id}",
    dependencies=[Depends(get_current_user)],
    response_model=PetReadWSearch,
)
async def read_pet_by_id(user_id: int, session: SessionDep):
    val_user_response(session.get)(User, user_id)  # type: ignore
    pet = val_pet_response(session.get, user_id)(Pet, pet_id)  # type: ignore

    return pet


@router.delete("/{pet_id}")
async def remove_pet(pet_id: int, current_user: CurrentUser, session: SessionDep):
    pet = val_pet_response(session.get, current_user.id)(Pet, pet_id)  # type: ignore
    session.delete(pet)
    session.commit()

    return Message(message="Pet deleted successfully")


@router.delete("/{pet_id}")
async def delete_pet(
    user_id: int, pet_id: int, session: SessionDep, current_user: CurrentUser
) -> Message:
    user = val_user_response(session.get)(User, user_id)  # type: ignore
    pet = val_pet_response(session.get, user.id)(Pet, pet_id)  # type: ignore

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions"
        )
    if user.id != pet.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pet does not belong to marked user",
        )

    session.delete(pet)
    session.commit()
    return Message(message="Pet deleted successfully")
