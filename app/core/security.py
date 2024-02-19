from datetime import datetime, timedelta

from jose import jwt
import bcrypt

if __name__ == "__main__":
    from config import settings
else:
    from app.core.config import settings

__all__ = ["create_access_token", "verify_pwd", "get_pwd_hash"]

ALGORITHM = "HS256"


def create_access_token(subject: int, expires_delta: timedelta | None = None):
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode = {"sub": str(subject), "exp": expire}

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def get_pwd_hash(pwd: str):
    pwd_bytes = pwd.encode()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed_pwd


def verify_pwd(plain_pwd: str, hashed_pwd: bytes):
    return bcrypt.checkpw(plain_pwd.encode(), hashed_pwd)
