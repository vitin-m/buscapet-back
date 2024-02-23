import datetime as dt
from enum import StrEnum
from typing import Union

from pydantic import AnyHttpUrl
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import SQLModel, Field, Relationship


class PetType(StrEnum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"


class PetBase(SQLModel):
    name: str
    kind: PetType
    breed: str | None = None
    fur_color: str | None = None
    size: str | None = None


class NewPet(PetBase):
    image: AnyHttpUrl


class Pet(PetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image: str

    # Pet -< User
    user_id: int = Field(default=None, foreign_key="user.id")
    user: Union["User", None] = Relationship(back_populates="pets")

    # Pet >- Search
    searches: list["Search"] = Relationship(back_populates="pet")


class PetRead(PetBase):
    id: int
    image: str


class PetReadWUser(PetRead):
    user: Union["UserRead", None] = None


class PetReadWSearch(PetRead):
    searches: list["SearchRead"] = []


class PetReadWUserSearch(PetReadWSearch, PetReadWUser):
    pass


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    phone: str = Field(unique=True, index=True)
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    image: str | None = None


class UserCreate(UserBase):
    password: str
    phone: PhoneNumber


class UserCreateOpen(SQLModel):
    username: str
    email: str
    full_name: str
    password: str


class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    password: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: bytes

    # User >- Search
    searches: list["Search"] = Relationship(back_populates="user")

    # User >- Pet
    pets: list["Pet"] = Relationship(back_populates="user")


class UserRead(UserBase):
    id: int


class UserReadWSearch(UserRead):
    searches: list["SearchReadWAll"] = []


class UserReadWPet(UserRead):
    pets: list["PetRead"] = []


class UserReadWSearchPet(UserReadWSearch, UserReadWPet):
    pass


class SightingBase(SQLModel):
    loc: str
    datetime: dt.datetime = Field(default=dt.datetime.utcnow())


class NewSighting(SightingBase):
    pass


class Sighting(SightingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Sighting -< Search
    search_id: int = Field(default=None, foreign_key="search.id")
    search: "Search" = Relationship(back_populates="sightings")


class SightingRead(SightingBase):
    pass


class SearchBase(SQLModel):
    created_at: dt.datetime = Field(default=dt.datetime.utcnow())
    poster: str
    is_active: bool = True


class NewSearch(SearchBase):
    sighting: Union[NewSighting, None]


class Search(SearchBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Search -< User
    user_id: int = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="searches")

    # Search -< Pet
    pet_id: int = Field(default=None, foreign_key="pet.id")
    pet: Pet = Relationship(back_populates="searches")

    # Search >- Sighting
    sightings: list[Sighting] = Relationship(back_populates="search")


class SearchUpdate(SQLModel):
    sighting: Union[NewSighting, None]
    poster: str | None
    is_active: bool = True


class SearchRead(SearchBase):
    id: int


class SearchReadWUser(SearchBase):
    user: Union[UserRead, None] = None


class SearchReadWPet(SearchBase):
    pet: Union[PetRead, None] = None


class SearchReadWUserPet(SearchReadWUser, SearchReadWPet):
    pass


class SearchReadWAll(SearchReadWUserPet):
    sightings: list[SightingRead] = []


# Security
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str


# Generic text
class Message(SQLModel):
    message: str = ""
