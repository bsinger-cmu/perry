import gym
from gym import spaces
import pygame
import numpy as np

class ToyEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    """
    Core functions
    """
    def __init__(self, 
                 render_mode=None, 
                 network="cage",
                 adversary="caldera_1",
                 control="tactic",
                 telemetry="sysflow",
                 techniques="all",
                 goal="CTF"):
        self.render_mode = render_mode
        self.network = network
        self.adversary_type = adversary
        self.control_level = control
        self.telemetry = telemetry
        self.techniques = techniques
        self.goal = goal

        # TODO: fix imports
        self.openstack_conn = initialize()
        self.manage_server, manage_ip = find_manage_server(self.openstack_conn)
        self.ansible_runner = AnsibleRunner(ssh_key_path, manage_ip, ansible_dir)
        self.cage_env = CageEnvironment(ansible_runner, self.openstack_conn)
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
        if self._check_precondition(action):
            target = self.actuators[action]["target"]
            self.actuators[action].run(target)
        
        terminated = False

        reward = self._get_reward()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info    

    """
    Customized functions
    """
    def _check_precondition(self, action):
        # TODO: check if the action is ready to be executed 
        return True
    
    def _check_termination(self):
        # TODO: define a termination condition
        return False

    def _get_reward(self):
        # TODO: reward shaping based on goals
        return 0