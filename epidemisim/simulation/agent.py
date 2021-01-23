import numpy as np
import enum
import random

MAX_X = 1000
MAX_Y = 1000
SICKNESS_PROXIMITY = 5
SICKNESS_DURATION = 500


class AgentStatus(enum.Enum):
    SUSCEPTIBLE = 1
    INFECTIOUS = 2
    IMMUNE = 3
    DEAD = 4


class Agent:

    def __init__(self, position: np.ndarray, velocity: np.ndarray):
        self.position = position
        self.velocity = velocity
        self.status = AgentStatus.SUSCEPTIBLE

        self.sickness_countdown = 0

    def calculate_death_chance(self):
        return 0.1

    def update(self):
        if self.status == AgentStatus.DEAD:
            return self

        self.position += self.velocity

        if self.position[0] < 0 or self.position[0] > MAX_X:
            self.velocity[0] *= -1
            self.position += self.velocity

        if self.position[1] < 0 or self.position[1] > MAX_Y:
            self.velocity[1] *= -1
            self.position += self.velocity

        if self.status == AgentStatus.INFECTIOUS:
            self.sickness_countdown -= 1

            if self.sickness_countdown == 0:
                if random.random() < self.calculate_death_chance():
                    self.status = AgentStatus.DEAD
                    self.velocity = np.array([0, 0])  # Oh no - we're dead D:
                else:
                    self.status = AgentStatus.IMMUNE  # Wahey - we're no longer sick!

        return self

    def make_sick(self):
        if self.status == AgentStatus.INFECTIOUS:
            return

        self.status = AgentStatus.INFECTIOUS
        self.sickness_countdown = SICKNESS_DURATION

    def is_near(self, agent):
        return np.linalg.norm(agent.position - self.position) < SICKNESS_PROXIMITY

    def __str__(self):
        return "AGENT:\tPOS({}, {})\tVEL({}, {})\tSTATUS({}, {})".format(
            self.position[0], self.position[1], self.velocity[0], self.velocity[1], self.status.name, self.sickness_countdown)


class Engine:

    def __init__(self, agents):
        self.agents = agents

    def tick(self):
        for agent in self.agents:
            agent.update()

        # self.agents = pool.map(Agent.update, self.agents)

        # pool.map(Agent.make_sick, [agent1
        #                           for agent1 in self.agents if agent1.status == AgentStatus.SUSCEPTIBLE
        #                           for agent2 in self.agents if agent2.status == AgentStatus.INFECTIOUS and agent1.is_near(agent2)])

        for agent1 in self.agents:
            if agent1.status == AgentStatus.SUSCEPTIBLE:
                for agent2 in self.agents:
                    if agent2.status == AgentStatus.INFECTIOUS and agent1.is_near(agent2):
                        agent1.make_sick()

        # for agent1 in self.agents:
        #    if agent1.status == AgentStatus.INFECTIOUS:
        #        for agent2 in self.agents:
        #            if agent2.status == AgentStatus.SUSCEPTIBLE and agent1.is_near(agent2):
        #                agent2.make_sick()


if __name__ == '__main__':
    import time

    a = Agent(np.array([10, 10]), np.array([0, 0]))
    b = Agent(np.array([20, 10]), np.array([-1, 0]))

    engine = Engine([a, b])

    while True:
        engine.tick()

        for agent in engine.agents:
            print(agent)

        print()
        time.sleep(0.2)
