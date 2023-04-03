import gymnasium as gym
from .emulator import Emulator

class GridWorldEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self):
        self.emulator = Emulator()
        self.emulator.start()

        self.started_attacker = False
        return
    
    def step(self, action):
        # If first step, start attacker
        if not self.started_attacker:
            self.emulator.start_attacker()

        # Run defender
        self.emulator.external_defender_steps(action)
        
        return

    def reset(self):
        self.emulator.start()
        self.started_attacker = False
        return
