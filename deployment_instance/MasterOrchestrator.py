from deployment_instance.orchestrators.caldera_orchestrator import CalderaOrchestrator
from deployment_instance.orchestrators.common_orchestrator import CommonOrchestrator
from deployment_instance.orchestrators.defender_orchestrator import DefenderOrchestrator
from deployment_instance.orchestrators.deployment_orchestrator import DeploymentOrchestrator
from deployment_instance.orchestrators.goal_orchestrator import GoalOrchestrator
from deployment_instance.orchestrators.vulnerability_orchestrator import VulnerabilityOrchestrator

# Master Orchestrator
class MasterOrchestrator():
    def __init__(self, ansible_runner) -> None:
        # Note: it might be useful to combine some of these orchestrators 
        self.common = CommonOrchestrator(ansible_runner)
        self.attacker = CalderaOrchestrator(ansible_runner)
        self.defender = DefenderOrchestrator(ansible_runner)
        self.deployment = DeploymentOrchestrator(ansible_runner)
        self.goals = GoalOrchestrator(ansible_runner)
        self.vulns = VulnerabilityOrchestrator(ansible_runner)