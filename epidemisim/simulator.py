import numpy as np
import enum
import random

from collections import Counter

TICKS_PER_SECOND = 20
MAX_X = 1000
MAX_Y = 1000
QUARANTINE_X = 200

PARAMETERS = {  # MINIMUM, DEFAULT, MAXIMUM
    'agents': (1, 200, 500),
    'initial_immunity': (0, 0, 100),

    'sickness_proximity': (1, 15, 30),
    'sickness_duration': (1, 250, 500),

    'quarantine_delay': (0, 249, 501),
    'distancing_factor': (0, 1, 100),
    'quarantining': (0, 0, 1)
}


class AgentStatus(enum.Enum):
    SUSCEPTIBLE = 1
    INFECTIOUS = 2
    IMMUNE = 3
    DEAD = 4


class Agent:

    def __init__(self, position: np.ndarray, velocity: np.ndarray, SICKNESS_DURATION: int, QUARANTINE_DELAY: int):
        self.SICKNESS_DURATION = SICKNESS_DURATION
        self.QUARANTINE_DELAY = QUARANTINE_DELAY

        self.position = position
        self.velocity = velocity
        self.status = AgentStatus.SUSCEPTIBLE
        self.sickness_countdown = 0
        self.quarantined = False

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
            self.velocity[0] *= -1.0
            self.position += self.velocity

        if self.position[1] < 0 or self.position[1] > MAX_Y:
            self.velocity[1] *= -1.0
            self.position += self.velocity

        if self.status == AgentStatus.INFECTIOUS:
            self.sickness_countdown -= 1

            if self.sickness_countdown == self.SICKNESS_DURATION - self.QUARANTINE_DELAY - 1:
                self.quarantined = True
                self.position = np.array([random.uniform(
                    MAX_X + 10, MAX_X + QUARANTINE_X), random.uniform(10, MAX_Y - 10)])
                self.velocity = np.array([0.0, 0.0])

            if self.sickness_countdown == 0:
                if random.random() < self.calculate_death_chance():
                    self.status = AgentStatus.DEAD  # Oh no - we're dead D:
                    self.velocity = np.array([0.0, 0.0])
                else:
                    self.status = AgentStatus.IMMUNE  # Wahey - we're no longer sick!
                    if self.quarantined:
                        self.quarantined = False
                        self.position = min(MAX_X, MAX_Y) * np.random.rand(2)
                        self.velocity = 5 * np.random.rand(2)

    def make_sick(self):
        if self.status == AgentStatus.INFECTIOUS:
            return

        self.status = AgentStatus.INFECTIOUS
        self.sickness_countdown = self.SICKNESS_DURATION

    def __str__(self):
        return "AGENT:\tPOS({}, {})\tVEL({}, {})\tSTATUS({}, {})".format(
            self.position[0], self.position[1], self.velocity[0], self.velocity[1], self.status.name, self.sickness_countdown)


class Engine:

    def __init__(self, n: int = 200, SICKNESS_PROXIMITY: int = 10,
                 SICKNESS_DURATION: int = 250,
                 DISTANCING_FACTOR: float = 0.01,
                 QUARANTINE_DELAY: int = 249,
                 DISTANCING_RADIUS_FACTOR: float = 1.5,
                 INITIAL_IMMUNITY: float = 0.0):
        self.SICKNESS_PROXIMITY = SICKNESS_PROXIMITY
        self.SICKNESS_DURATION = SICKNESS_DURATION
        self.DISTANCING_FACTOR = DISTANCING_FACTOR
        self.QUARANTINE_DELAY = QUARANTINE_DELAY
        self.DISTANCING_RADIUS_FACTOR = DISTANCING_RADIUS_FACTOR

        self.agents = self.create_agents(n, INITIAL_IMMUNITY)
        self.agent_count = n
        self.stats = {
            AgentStatus.DEAD.name: 0,
            AgentStatus.IMMUNE.name: 0,
            AgentStatus.INFECTIOUS.name: 1,
            AgentStatus.SUSCEPTIBLE.name: n - 1
        }
        self.ticks = 0

    def create_agents(self, n, immunity):
        m = min(MAX_X, MAX_Y)
        agents = [Agent(m * np.random.rand(2), 5 * np.random.rand(2), self.SICKNESS_DURATION, self.QUARANTINE_DELAY)
                  for _ in range(n)]

        agents[-1].make_sick()
        for i in range(int(n * immunity)):
            agents[i].status = AgentStatus.IMMUNE

        return agents

    def tick(self):
        self.ticks += 1

        positions = []
        statuses = []
        for agent in self.agents:
            agent.update()
            positions.append(agent.position)
            statuses.append(agent.status.name)

        self.stats = dict(Counter(statuses))
        if self.stats.get(AgentStatus.INFECTIOUS.name, 0) <= 0:
            return

        positions = np.array(positions)
        differences = positions.reshape(-1, 1, 2) - positions
        norms = np.linalg.norm(differences, axis=2)
        for i in range(self.agent_count):
            for j in range(i + 1, self.agent_count):
                if norms[i, j] < self.DISTANCING_RADIUS_FACTOR * self.SICKNESS_PROXIMITY:
                    acceleration = self.DISTANCING_FACTOR * \
                        differences[i, j] / norms[i, j]**2

                    self.agents[i].velocity -= acceleration
                    self.agents[j].velocity += acceleration

                    if self.agents[i].status == AgentStatus.SUSCEPTIBLE \
                            and self.agents[j].status == AgentStatus.INFECTIOUS \
                            and norms[i, j] < self.SICKNESS_PROXIMITY:
                        self.agents[i].make_sick()
