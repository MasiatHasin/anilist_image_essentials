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
    num_colors: int = 10


class ImageCreate(BaseModel):
    name: str
    url: str
    type: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str


class UserView(BaseModel):
    id: int
    username: str


class User(UserView):
    username: str
    settings: Optional[Settings] = {}
    images: Optional[List[ImageCreate]] = []

    class Config:
        orm_mode = True
