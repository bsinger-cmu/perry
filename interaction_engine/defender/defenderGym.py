import gym
from gym import spaces
import pygame
import numpy as np

class ToyEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, 
                 render_mode=None, 
                 network="cage",
                 adversary="caldera_1",
                 control="tactic",
                 telemetry="sysflow",
                 techniques="all",
                 goal="CTF"):
        # TODO: fix imports
        self.conn = initialize()
        self.manage_server, manage_ip = find_manage_server(conn)
        self.ansible_runner = AnsibleRunner(ssh_key_path, manage_ip, ansible_dir)
        self.cage_env = CageEnvironment(ansible_runner, conn)
        self.cage_env.setup()

        # Setup initial attacker
        self.attack_params = {'host': '192.168.199.3', 'user': 'ubuntu', 'caldera_ip': caldera_ip}
        r = self.ansible_runner.run_playbook('caldera/install_attacker.yml', playbook_params=params)
        self.attacker = Attacker(caldera_api_key)

        # Start the telemetry server
        self.telemetry_server = TelemetryServer('TelemetryServer', self.handle_telemetry_event)
        self.telemetry_server.start()

        self.observation_space = spaces.Dict(
            {
                "alerts": spaces.Box(0, 10, shape=(2,), dtype=int),
                # "attacker": spaces.Box(0, 10, shape=(2,), dtype=int),
            }
        )

        # We need a few more actions
        self.action_space = spaces.Discrete(4)

        self.actuators = {
            1: {"action": StartHoneyService(self.ansible_runner, self.openstack_conn), "target": '192.168.200.3'},
            2: {"action": ShutdownServer(self.ansible_runner, self.openstack_conn), "target": '192.168.200.3'}
        }

    def _get_obs(self):
        # TODO: convert telemetry events to observation matrix
        return {"alerts": []}
    
    def _get_info(self):
        return {"trajectory": []}
    
    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()
        
    def step(self, action):
        # Map the action (element of {0,1,2,3}) to an actual action
        target = self.actuators[action]["target"]
        self.actuators[action].run(target)
        
        terminated = False
        reward = 0
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info    
