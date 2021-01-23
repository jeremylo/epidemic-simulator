import numpy as np
import multiprocessing as mp

from functools import partial
from bokeh.layouts import gridplot
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.models import ColumnDataSource

from simulation.agent import Agent, Engine, AgentStatus, MAX_X, MAX_Y

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


agents = create_agents(500)
engine = Engine(agents)

data = {'color': ['blue'] * len(agents)}
data['x'], data['y'] = separate_positions(agents)
source = ColumnDataSource(data)

p = figure(title="Simulation", x_axis_label='x',
           y_axis_label='y', x_range=(0, MAX_X), y_range=(0, MAX_Y), tools="")
p.scatter(x='x', y='y', color='color', line_width=2, source=source)


def update():
    engine.tick()
    s = slice(len(agents))
    data['x'] = [a.position[0] for a in agents]
    data['y'] = [a.position[1] for a in agents]
    data['color'] = [COLORS[a.status] for a in agents]

    source.patch({
        'x': [(s, data['x'])],
        'y': [(s, data['y'])],
        'color': [(s, data['color'])]
    })


curdoc().add_root(
    gridplot([[p]], toolbar_location="left"))

curdoc().add_periodic_callback(partial(update), 50)
