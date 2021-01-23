import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from epidemisim.simulation.agent import Agent, Engine, AgentStatus


def create_agents(n=10):
    return [Agent(*(200 * np.random.rand(1, 2)), *
                  (5 * np.random.rand(1, 2))) for i in range(n)]


def update(agent):
    agent.update()
    return (agent.position[0], agent.position[1])


def animate(i):
    engine.tick()

    mat.set_offsets(np.c_[
        [a.position[0] for a in agents], [a.position[1] for a in engine.agents]
    ])

    mat.set_color([
        'red' if a.status == AgentStatus.INFECTIOUS else 'green' for a in engine.agents
    ])

    return mat,


if __name__ == '__main__':
    agents = create_agents(10)
    engine = Engine(agents)

    fig, ax = plt.subplots()
    ax.axis([0, 200, 0, 200])

    mat = ax.scatter([a.position[0] for a in agents],
                     [a.position[1] for a in agents])

    ani = animation.FuncAnimation(fig, animate, interval=50)
    plt.show()
