import numpy as np
import random
import pandas as pd
from datetime import datetime
import os

class RouletteEnvironment:
    def __init__(self, data):
        self.data = data
        self.current_step = 0

    def reset(self):
        self.current_step = 0
        return self.data.iloc[self.current_step].values

    def step(self, action):
        self.current_step += 1
        if self.current_step >= len(self.data):
            self.current_step = 0
        reward = 1 if self.data.iloc[self.current_step]['number'] == action else -1
        done = self.current_step == len(self.data) - 1
        return self.data.iloc[self.current_step].values, reward, done

def create_q_table(env):
    state_space_size = len(env.data.columns)
    action_space_size = 37  # Numbers 0-36
    return np.zeros((state_space_size, action_space_size))

def choose_action(state, q_table, epsilon):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, 36)
    else:
        return np.argmax(q_table[state])

def train_q_learning(env, q_table, episodes=1000, alpha=0.1, gamma=0.6, epsilon=0.1):
    for episode in range(episodes):
        state = env.reset()
        done = False
        while not done:
            action = choose_action(state, q_table, epsilon)
            next_state, reward, done = env.step(action)
            old_value = q_table[state, action]
            next_max = np.max(q_table[next_state])
            new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
            q_table[state, action] = new_value
            state = next_state

    return q_table

def main(server_name):
    data_path = os.path.join('/home/user/DB/model/cleaned_data', f'{server_name}_cleaned_data.csv')
    data = pd.read_csv(data_path)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['hour'] = data['timestamp'].dt.hour
    data['minute'] = data['timestamp'].dt.minute
    data['day_of_week'] = data['timestamp'].dt.dayofweek
    data['is_weekend'] = data['timestamp'].dt.dayofweek >= 5
    env = RouletteEnvironment(data)
    q_table = create_q_table(env)
    q_table = train_q_learning(env, q_table)
    np.save(f'/home/user/DB/model/q_tables/{server_name}_q_table.npy', q_table)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Server name not provided.")
