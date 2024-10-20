from pydantic import BaseModel


class DefenderInformation(BaseModel):
    telemetry: str
    strategy: str
    capabilities: dict[str, int]


class AttackerInformation(BaseModel):
    name: str


class DeploymentInstanceInformation(BaseModel):
    name: str


class Scenario(BaseModel):
    name: str
    defender: DefenderInformation
    attacker: AttackerInformation
    deployment_instance: DeploymentInstanceInformation


class Experiment(BaseModel):
    name: str
    trials: int
    scenario: str
    timeout: int = 75
