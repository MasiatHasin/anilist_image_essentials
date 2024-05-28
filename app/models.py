from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from . import database

Base = database.Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    current_color = Column(String(50), nullable=True)

    owner_setting = relationship("User", back_populates="settings", uselist=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    anilist_id = Column(String(50))

    settings = relationship("Setting", back_populates="owner_setting", uselist=False)
    activities = relationship("Activity", back_populates="owner_activity")
    images = relationship("Image", back_populates="owner_image")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    activity_id = Column(Integer)

    owner_activity = relationship("User", back_populates="activities")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(50))
    url = Column(String(50))

    owner_image = relationship("User", back_populates="images")
