import numpy as np


class Agent:

    def __init__(self, position: np.ndarray, velocity: np.ndarray):
        self.position = position
        self.velocity = velocity

    def update(self):
        self.position += self.velocity


if __name__ == '__main__':

    import time

    a = Agent(np.array([0, 0]), np.array([2, 1]))
    b = Agent(np.array([5, -3]), np.array([-1, 1]))

    agents = [a, b]

    while True:
        i = 0
        for agent in agents:
            agent.update()
            print(i, agent.position, agent.velocity)
            i += 1

        time.sleep(0.1)
