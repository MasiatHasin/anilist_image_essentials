from pydantic import BaseModel
from typing import Dict, Optional, List
from pydantic import HttpUrl


class Settings(BaseModel):
    id: int
    owner_id: int
    current_colors: str

    class Config:
        orm_mode = True


class ExtractColors(BaseModel):
    username: str
    password: str
    image_url: HttpUrl
    num_colors: int | None = 5


class ImageUser(BaseModel):
    username: str

    class Config:
        orm_mode = True


class ImageCreate(ImageUser):
    name: str
    url: str
    type: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str
    anilist_name: str


class UserView(BaseModel):
    id: int
    username: str
    anilist_name: str


class User(UserView):
    username: str
    settings: Optional[Settings] = {}
    images: Optional[List[ImageCreate]] = []

    class Config:
        orm_mode = True
