from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from . import database

Base = database.Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    current_colors = Column(String(50), nullable=True)

    owner_setting = relationship("User", back_populates="settings", uselist=False)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(50))
    url = Column(String(50))
    type = Column(Integer)

    owner_image = relationship("User", back_populates="images")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    anilist_name = Column(String(50))

    images = relationship("Image", back_populates="owner_image", cascade="all, delete")
    settings = relationship(
        "Setting", back_populates="owner_setting", cascade="all, delete", uselist=False
    )
