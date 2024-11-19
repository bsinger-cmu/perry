from pydantic import BaseModel
from enum import Enum
from typing import Optional


class Abstraction(Enum):
    HIGH_LEVEL = "high"
    LOW_LEVEL = "low"
    NO_ABSTRACTION = "none"


class AttackerConfig(BaseModel):
    name: str
    strategy: str
    environment: str
    abstraction: Optional[Abstraction] = Abstraction.HIGH_LEVEL
