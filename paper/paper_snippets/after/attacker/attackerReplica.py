# Ignore type hinting
# type: ignore
import random

from HighLevelActions import (
    InfectHost,
    ScanNetwork,
    DiscoverHostInformation,
    ExfiltrateData,
)
from EnvironmentStateService import EnvironmentStateService
from HighLevelObservations import TelemetryModule


# (1) Gain initial access to Equifax network
# Use attacker host to scan external network
subnets_to_scan = EnvironmentStateService.get_all_subnets()
await ScanNetwork(subnets_to_scan).execute()
# Try to infect all hosts on external network
for target_host in EnvironmentStateService.get_all_hosts():
    attack_paths = EnvironmentStateService.get_attack_paths_to_target(target_host)
    for attack_path in attack_paths:
        await InfectHost(attack_path).execute()

# (2) Find and use any credentials
for infected_host in EnvironmentStateService.get_infected_hosts():
    # Discover information about host
    await DiscoverHostInformation(initial_access_host).execute()

    # Use any found credentials to infect other hosts
    attack_paths = EnvironmentStateService.get_attack_paths_from_host(
        infected_host, only_credential_paths=True
    )
    for attack_path in attack_paths:
        await InfectHost(attack_path).execute()

# (3) Exfiltrate data any discovered data
for infected_host in EnvironmentStateService.get_infected_hosts():
    # Discover information about host
    events = await DiscoverHostInformation(initial_access_host).execute()

    # If found critical data, exfiltrate data
    if TelemetryModule.found_critical_data(events):
        # Try to exfiltrate data from infected host to attacker host
        await ExfiltrateData(infected_host)
