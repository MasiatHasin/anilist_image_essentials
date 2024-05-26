from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from . import database

Base = database.Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    current_color = Column(String(50), nullable=True)

    owner_setting = relationship("User", back_populates="settings", uselist=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    anilist_name = Column(String(50))

    settings = relationship(
        "Setting", back_populates="owner_setting", cascade="all, delete", uselist=False
    )
    activities = relationship(
        "Activity", back_populates="owner_activity", cascade="all, delete"
    )


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    activity_id = Column(Integer)

    owner_activity = relationship("User", back_populates="activities")
