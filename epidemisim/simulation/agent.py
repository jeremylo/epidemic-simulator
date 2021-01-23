import numpy as np
import itertools

MAX_X = 200
MAX_Y = 200
SICKNESS_PROXIMITY = 5
SICKNESS_DURATION = 50


class Agent:

    def __init__(self, position: np.ndarray, velocity: np.ndarray):
        self.position = position
        self.velocity = velocity

        self.is_sick = False
        self.sickness_countdown = 0

    def update(self):
        self.position += self.velocity

        if self.position[0] < 0 or self.position[0] > MAX_X:
            self.velocity[0] *= -1
            self.position += self.velocity

        if self.position[1] < 0 or self.position[1] > MAX_Y:
            self.velocity[1] *= -1
            self.position += self.velocity

        if self.is_sick:
            self.sickness_countdown -= 1

            if self.sickness_countdown == 0:
                self.is_sick = True  # Wahey - we're no longer sick!

    def make_sick(self):
        self.is_sick = True
        self.sickness_countdown = SICKNESS_DURATION

    def is_near(self, agent):
        return np.linalg.norm(agent.position - self.position) < SICKNESS_PROXIMITY

    def __str__(self):
        return "AGENT:\tPOS({}, {})\tVEL({}, {})\tSICK({}, {})".format(
            self.position[0], self.position[1], self.velocity[0], self.velocity[1], self.is_sick, self.sickness_countdown)


class Engine:

    def __init__(self, agents):
        self.agents = agents

    def tick(self):
        for agent in self.agents:
            agent.update()

        for agent1, agent2 in itertools.combinations(filter(lambda agent: not agent.is_sick, self.agents), 2):
            if agent1.is_near(agent2):
                agent1.make_sick()
                agent2.make_sick()


if __name__ == '__main__':

    import time

    a = Agent(np.array([10, 10]), np.array([-4, 1]))
    b = Agent(np.array([20, 10]), np.array([-1, 6]))

    engine = Engine([a, b])

    while True:
        engine.tick()

        for agent in engine.agents:
            print(agent)

        print()
        time.sleep(0.2)
