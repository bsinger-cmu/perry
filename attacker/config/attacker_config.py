from pydantic import BaseModel
from enum import Enum


# Enum of environments
class Environment(Enum):
    EQUIFAX_LARGE = "equifax_large"
    ICS = "ics"
    RING = "ring"


class AttackerConfig(BaseModel):
    name: str
    strategy: str
    environment: Environment
