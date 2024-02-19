from datetime import datetime
import functools
from typing import Annotated, Callable, Union
import aiofiles

from pydantic import ValidationError
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from jose import jwt, JWTError

from app.core import security
from app.core.config import settings
from app.db.engine import engine
from app.models import Pet, TokenPayload, User


def val_user_response(fn: Callable[..., Union[User, None]], user_id: int | None = None):
    @functools.wraps(fn)
    def val_user_res_deco(*args, **kwargs):
        user = fn(*args, **kwargs)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        if not user.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Inactive user")
        if user_id is not None and user.id != user_id and not user.is_superuser:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Not enough permissions')
        return user
    return val_user_res_deco

def val_pet_response(fn: Callable[..., Union[Pet, None]], user_id: int | None = None):
    @functools.wraps(fn)
    def val_pet_res_deco(*args, **kwargs):
        pet = fn(*args, **kwargs)
        if not pet:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Pet not found")
        if user_id is not None and not pet.user_id == user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Pet not owned by user")
        return pet
    return val_pet_res_deco


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PATH}/login/token")

def get_db():
    with Session(engine) as session:
        yield session


TokenDep = Annotated[str, Depends(oauth2_scheme)]
SessionDep = Annotated[Session, Depends(get_db)]

def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Could not validate credentials")
    user = val_user_response(session.get)(User, token_data.sub)  # type: ignore
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user: CurrentUser):
    if not current_user.is_superuser:
        HTTPException(
            status.HTTP_401_UNAUTHORIZED, "User doesn't have enough privileges"
        )
    return current_user

async def save_image(*, img: UploadFile, deco_str: str):
    image_name = (
        f'{'_'.join(deco_str.split())}'
        f'_{int(datetime.utcnow().timestamp())}.'
        f'{img.filename.split('.')[-1] if img.filename else 'corrupted'}'
    )
    image_path = settings.STATIC_PATH.joinpath(image_name)
    
    async with aiofiles.open(image_path, 'wb') as out_file:
        while content := await img.read(8 * 1024):
            await out_file.write(content)
    
    # TODO: append server name, server host
    image_link = f'{settings.API_PATH}/static/{image_name}'
    return image_link
