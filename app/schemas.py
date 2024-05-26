from pydantic import BaseModel
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
    anilist_name: str


class UserView(BaseModel):
    id: int
    username: str
    anilist_name: str


class User(UserView):
    username: str
    anilist_name: str
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
