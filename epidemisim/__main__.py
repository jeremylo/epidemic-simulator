import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import multiprocessing as mp

from epidemisim.simulation.agent import Agent, Engine, AgentStatus, MAX_X, MAX_Y


COLORS = {
    AgentStatus.SUSCEPTIBLE: 'blue',
    AgentStatus.INFECTIOUS: 'red',
    AgentStatus.IMMUNE: 'green',
    AgentStatus.DEAD: 'black'
}


def create_agents(n=10):
    m = min(MAX_X, MAX_Y)
    sick_agent = Agent(m * np.random.rand(2), 5 * np.random.rand(2))
    sick_agent.make_sick()
    return [Agent(m * np.random.rand(2), 5 * np.random.rand(2)) for i in range(n - 1)] + [sick_agent]


def separate_positions(agents):
    xs = []
    ys = []
    for agent in agents:
        xs.append(agent.position[0])
        ys.append(agent.position[1])
    return xs, ys


def animate(i, pool):
    engine.tick(pool)

    mat.set_offsets([agent.position for agent in engine.agents])
    mat.set_color([COLORS[agent.status] for agent in engine.agents])

    return mat,


if __name__ == '__main__':
    agents = create_agents(200)
    engine = Engine(agents)

    fig, ax = plt.subplots()
    ax.axis([0, MAX_X, 0, MAX_Y])

    mat = ax.scatter(*separate_positions(agents))

    with mp.Pool(processes=10) as pool:
        ani = animation.FuncAnimation(
            fig, animate, fargs=(pool, ), interval=10)
        plt.show()
