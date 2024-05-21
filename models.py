from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON

from .database import Base


class settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    current_color = Column(String)
    color_definition_id = Column(Integer, ForeignKey("color_profiles.id"))


class ColorProfiles(Base):
    __tablename__ = "color_profiles"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    color_definition = Column(JSON)
