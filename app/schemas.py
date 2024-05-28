from pydantic import BaseModel, AnyUrl
from typing import Dict, Optional, List
from pydantic import HttpUrl


class Settings(BaseModel):
    id: int
    owner_id: int
    current_color: str | None = None

    class Config:
        orm_mode = True


class UserCred(BaseModel):
    username: str
    password: str


class UserCreate(UserCred):
    anilist_id: str


class UserView(BaseModel):
    id: int
    username: str
    anilist_id: str


class User(UserView):
    username: str
    anilist_id: str
    settings: Optional[Settings] = {}

    class Config:
        orm_mode = True


class ActivityCreate(BaseModel):
    user: UserCred
    activity_id: int

    class Config:
        orm_mode = True


class Activity(BaseModel):
    id: int
    owner_id: int
    activity_id: int


class ImageCreate(BaseModel):
    user: UserCred
    name: str
    url: AnyUrl

    class Config:
        orm_mode = True


class Image(BaseModel):
    id: int
    owner_id: int
    name: str
    url: AnyUrl
