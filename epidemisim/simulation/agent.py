import numpy as np
import enum
import random

from collections import Counter

MAX_X = 1000
MAX_Y = 1000
SICKNESS_PROXIMITY = 10
SICKNESS_DURATION = 150


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

        # This roughly fits an estimate for Covid-19 mortality by age
        self.age = random.randint(18, 100)
        # Data used to fit the exponential:
        # 40yr -> 0.3% chance
        # 50yr -> 0.4% chance
        # 60yr -> 1.0% chance
        # 70yr -> 3.5% chance
        # 80yr -> 13.% chance
        # 90yr -> 20.% chance

        self.comorbity = 0.75 + max(0.5 * random.random(), 0.15)
        self.frailty = max(
            min(min(0.0000503 * 1.09792**self.age, 1) * self.comorbity, 1), 0)

    def calculate_death_chance(self):
        return self.frailty

    def update(self):
        if self.status == AgentStatus.DEAD:
            return

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
        self.agent_count = len(agents)
        self.stats = {
            AgentStatus.DEAD.name: 0,
            AgentStatus.IMMUNE.name: 0,
            AgentStatus.INFECTIOUS.name: 1,
            AgentStatus.SUSCEPTIBLE.name: len(agents) - 1
        }
        self.ticks = 0

    def tick(self):
        self.ticks += 1

        statuses = []
        for agent in self.agents:
            agent.update()
            statuses.append(agent.status.name)

        self.stats = dict(Counter(statuses))

        if self.stats.get(AgentStatus.INFECTIOUS.name, 0) <= 0:
            return

        positions = np.empty((self.agent_count, self.agent_count, 2))
        for i in range(self.agent_count):
            for j in range(i + 1, self.agent_count):
                positions[i, j] = self.agents[j].position - \
                    self.agents[i].position

        norms = np.linalg.norm(positions, axis=2)

        for i in range(self.agent_count):
            if self.agents[i].status == AgentStatus.SUSCEPTIBLE:
                for j in range(i + 1, self.agent_count):
                    # if norms[i, j] < 2 * SICKNESS_PROXIMITY:
                    #    self.agents[i].velocity -= 0.05 * positions[i, j]
                    #    self.agents[j].velocity += 0.05 * positions[i, j]

                    if self.agents[j].status == AgentStatus.INFECTIOUS and norms[i, j] < SICKNESS_PROXIMITY:
                        self.agents[i].make_sick()


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
