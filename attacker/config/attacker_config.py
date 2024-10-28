from pydantic import BaseModel


class AttackerConfig(BaseModel):
    name: str
    strategy: str
    environment: str
    abstraction: str
