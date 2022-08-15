from agents.SimpleAttacker import SimpleAttacker
from environment.Environment import Environment
from environment.Host import Host

def main():
    # Setup attacker
    attacker = SimpleAttacker()

    # Setup environment
    env = Environment()
    
    # Create host for attacker to have initial access to
    compromised_host = Host('host 1', 'ip_addr')

    env.attackers.append(attacker)
    env.attacker_hosts[attacker] = compromised_host
