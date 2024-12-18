from pydantic import BaseModel
from enum import Enum
from typing import Optional


class AbstractionLevel(str, Enum):
    HIGH_LEVEL = "high"
    LOW_LEVEL = "low"
    NO_ABSTRACTION = "none"
    NO_SERVICES = "no_services"


class AttackerConfig(BaseModel):
    name: str
    strategy: str
    environment: str
    abstraction: Optional[AbstractionLevel] = AbstractionLevel.HIGH_LEVEL

    class Config:
        # Enums are serialized as their values
        use_enum_values = True
