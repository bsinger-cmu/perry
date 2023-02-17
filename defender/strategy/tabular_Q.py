import numpy as np 

class IndependentQAgent():
    def __init__(self, env, idx):
        self.q = {}
        self.epsilon = 0.1 
        self.env = env
        self.lr = 0.001 
        self.gamma = 0.95 
        self.index = idx

    def update(self, state, action, reward, next_state):
        self.update_q(state, action, reward, next_state)
        
    def update_q(self, state_n, action_n, reward_n, next_state_n):
        state_key = self.state_to_key(state_n[self.index])
        next_state_key = self.state_to_key(next_state_n[self.index])
        action = action_n[self.index]
        reward = reward_n[self.index]

        self.init_dicts(state_key, action, next_state_key)
        old_q = self.q[state_key][action]
        lr = self.lr 
        q_val = (1 - lr) * old_q + lr * (reward + self.gamma * self.v(next_state_key))
        self.q[state_key][action] = q_val

    def init_dicts(self, state_key, action_key, next_state_key):
        # initialize if not alrady in dict
        if state_key not in self.q.keys():
            self.q[state_key] = {}
        if next_state_key not in self.q.keys():
            self.q[next_state_key] = {}
        if action_key not in self.q[state_key].keys():
            self.q[state_key][action_key] = 0.
        if action_key not in self.q[next_state_key].keys():
            self.q[next_state_key][action_key] = 0.

    def v(self, state_key):
        possible_actions = list(self.q[state_key].keys())
            
        action = max(possible_actions)
        action = max(self.q[state_key], key=self.q[state_key].get)
        if action not in self.q[state_key].keys():
            self.q[state_key][action] = -5.
        return self.q[state_key][action]     

    def state_to_key(self, state):
        key_state = tuple(np.array(state).tobytes())
        return key_state
    
    def action(self, state):
        return self.get_action(state)

    def get_action(self, state):
        if np.random.random() < self.epsilon:
            return self.env.action_space[self.index].sample()
        else:
            state_key = self.state_to_key(state)
            if state_key in self.q.keys():
                return max(self.q[state_key], key=self.q[state_key].get)
            else:
                return self.env.action_space[self.index].sample()