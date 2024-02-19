from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db import crud
from app.core import security
from app.core.config import settings
from app.models import Message, NewPassword, Token, UserRead
from ..deps import SessionDep, CurrentUser, val_user_response

router = APIRouter()


@router.post("/token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = val_user_response(crud.authenticate)(
        session, form_data.username, form_data.password
    )

    token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=token_expire  # type:ignore
    )

    return Token(access_token=access_token)


@router.post("/test-token", response_model=UserRead)
def test_token(current_user: CurrentUser):
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(session: SessionDep, email: str):
    val_user_response(crud.get_user_by_email)(session, email)
    # Mockado
    return Message(message="Recovery email sent")
