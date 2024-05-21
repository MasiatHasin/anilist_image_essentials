from pydantic import BaseModel
from typing import Dict

class Settings(BaseModel):
    name: str
    current_color: str
    color_definition: Dict[str, float]