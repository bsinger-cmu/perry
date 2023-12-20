from pydantic import BaseModel
from scenarios.Scenario import Scenario
import enum


class FlagType(enum.Enum):
    USER = ("user",)
    ROOT = ("root",)


class FlagInformation(BaseModel):
    flag: str
    host: str
    type: FlagType
    time_found: float


class ExperimentResult(BaseModel):
    scenario: Scenario
    experiment_time: float
    execution_time: float
    setup_time: float
    flags_captured: list[FlagInformation]
    data_exfiltrated: list[str]
    hosts_infected: list[str]
    operation_id: str
