import numpy as np
import multiprocessing as mp

from functools import partial
from bokeh.layouts import gridplot
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.models import ColumnDataSource
from bokeh.colors import RGB

from simulation.agent import Agent, Engine, AgentStatus, MAX_X, MAX_Y


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

p = figure(title="Epidemic Simulation", x_range=(
    0, MAX_X), y_range=(0, MAX_Y), tools="")

p.scatter(x='x', y='y', color='color', line_width=2, source=source)
p.axis.visible = False
p.xgrid.visible = False
p.ygrid.visible = False


def get_color(agent):
    if agent.status == AgentStatus.DEAD:
        return '#718093'  # 2f3640
    elif agent.status == AgentStatus.IMMUNE:
        return '#44bd32'
    elif agent.status == AgentStatus.INFECTIOUS:
        return RGB(232, 65, 24).lighten(agent.frailty).to_css()
    elif agent.status == AgentStatus.SUSCEPTIBLE:
        return RGB(0, 168, 255).lighten(agent.frailty).to_css()


def update():
    engine.tick()
    s = slice(len(agents))
    data['x'] = [a.position[0] for a in agents]
    data['y'] = [a.position[1] for a in agents]
    data['color'] = [get_color(a) for a in agents]

    source.patch({
        'x': [(s, data['x'])],
        'y': [(s, data['y'])],
        'color': [(s, data['color'])]
    })


curdoc().add_root(
    gridplot([[p]], toolbar_location="left"))

curdoc().add_periodic_callback(partial(update), 50)
