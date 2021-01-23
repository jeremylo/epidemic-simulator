import numpy as np
import itertools

MAX_X = 200
MAX_Y = 200
SICKNESS_PROXIMITY = 5


class Agent:

    def __init__(self, position: np.ndarray, velocity: np.ndarray):
        self.position = position
        self.velocity = velocity
        self.is_sick = False

    def update(self):
        self.position += self.velocity

        if self.position[0] < 0 or self.position[0] > MAX_X:
            self.velocity[0] *= -1
            self.position += self.velocity

        if self.position[1] < 0 or self.position[1] > MAX_Y:
            self.velocity[1] *= -1
            self.position += self.velocity

    def is_near(self, agent):
        return np.linalg.norm(agent.position - self.position) < SICKNESS_PROXIMITY

    def __str__(self):
        return "AGENT:\tPOS({}, {})\tVEL({}, {})\tSICK({})".format(
            self.position[0], self.position[1], self.velocity[0], self.velocity[1], self.is_sick)


if __name__ == '__main__':

    import time

    a = Agent(np.array([10, 10]), np.array([0, 0]))
    b = Agent(np.array([20, 10]), np.array([-1, 0]))

    agents = [a, b]

    while True:
        for agent in agents:
            agent.update()

        for agent1, agent2 in itertools.combinations(agents, 2):
            if agent1.is_near(agent2):
                agent1.is_sick = True
                agent2.is_sick = True

        for agent in agents:
            print(agent)

        print()
        time.sleep(0.2)
