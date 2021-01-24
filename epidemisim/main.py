import numpy as np
import multiprocessing as mp
import pandas as pd

from bokeh.layouts import gridplot
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.models import ColumnDataSource
from bokeh.colors import RGB
from bokeh.models import DataRange1d

from simulation.agent import Agent, Engine, AgentStatus, MAX_X, MAX_Y, QUARANTINE_X


def get_color(agent):
    if agent.status == AgentStatus.DEAD:
        return RGB(113, 128, 147).lighten(agent.frailty).to_css()  # 718093
    elif agent.status == AgentStatus.IMMUNE:
        return RGB(68, 189, 50).lighten(agent.frailty).to_css()  # 44bd32
    elif agent.status == AgentStatus.INFECTIOUS:
        return RGB(232, 65, 24).lighten(agent.frailty).to_css()  # e84118
    elif agent.status == AgentStatus.SUSCEPTIBLE:
        return RGB(0, 168, 255).lighten(agent.frailty).to_css()  # 00a8ff


def summarise(agents):
    xs = []
    ys = []
    colors = []
    for agent in agents:
        xs.append(agent.position[0])
        ys.append(agent.position[1])
        colors.append(get_color(agent))
    return xs, ys, colors


def update():
    engine.tick()

    s = slice(engine.agent_count)
    data['x'], data['y'], data['color'] = summarise(engine.agents)

    source.patch({
        'x': [(s, data['x'])],
        'y': [(s, data['y'])],
        'color': [(s, data['color'])]
    })

    status_source.stream({
        "index": [engine.ticks],
        AgentStatus.DEAD.name: [engine.stats.get(AgentStatus.DEAD.name, 0)],
        AgentStatus.IMMUNE.name: [engine.stats.get(AgentStatus.IMMUNE.name, 0)],
        AgentStatus.INFECTIOUS.name: [engine.stats.get(AgentStatus.INFECTIOUS.name, 0)],
        AgentStatus.SUSCEPTIBLE.name: [engine.stats.get(AgentStatus.SUSCEPTIBLE.name, 0)],
    })


# Simulation

AGENT_COUNT = 500
engine = Engine(AGENT_COUNT)

data = {}
data['x'], data['y'], data['color'] = summarise(engine.agents)
source = ColumnDataSource(data)

p = figure(title="Epidemic Simulation", x_axis_label='x',
           y_axis_label='y', x_range=(0, MAX_X + QUARANTINE_X), y_range=(0, MAX_Y), tools="")
p.scatter(x='x', y='y', color='color', line_width=2, source=source)
p.line([MAX_X + 5, MAX_X + 5], [0, MAX_Y], line_width=2, color='#eeeeee')
p.axis.visible = False
p.xgrid.visible = False
p.ygrid.visible = False


# Status Graph

names = [AgentStatus.DEAD.name, AgentStatus.IMMUNE.name,
         AgentStatus.INFECTIOUS.name, AgentStatus.SUSCEPTIBLE.name]

status_source = ColumnDataSource(pd.DataFrame(np.zeros((1, 4)), columns=names))

p2 = figure(title="Population Health",
            x_range=DataRange1d(start=0, bounds=(0, None)),
            y_range=(0, AGENT_COUNT))
p2.grid.minor_grid_line_color = '#eeeeee'
p2.varea_stack(stackers=names, x='index',
               color=('#718093', '#44bd32', '#e84118', '#00a8ff'), legend_label=names, source=status_source)
p2.legend.items.reverse()

# Plot to page

curdoc().add_root(
    gridplot([[p, p2]], toolbar_location="left"))

curdoc().add_periodic_callback(update, 50)
