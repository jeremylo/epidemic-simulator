import numpy as np
import pandas as pd

from bokeh.layouts import gridplot, column
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.colors import RGB
from bokeh.models import DataRange1d, Slider, Toggle, Div, CustomJS

from .simulator import Engine, AgentStatus, MAX_X, MAX_Y, QUARANTINE_X, TICKS_PER_SECOND
from .visualiser import get_about_us, get_controls

TERMINATING = False
DEFAULT_PARAMETERS = {  # MINIMUM, DEFAULT, MAXIMUM
    'agents': (1, 200, 500),
    'initial_immunity': (0, 0, 100),

    'sickness_proximity': (1, 15, 30),
    'sickness_duration': (1, 250, 500),

    'quarantine_delay': (0, 249, 501),
    'distancing_factor': (0, 1, 100),
    'quarantining': (0, 0, 1)
}


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
    xs, ys, colors = [], [], []
    for agent in agents:
        xs.append(agent.position[0])
        ys.append(agent.position[1])
        colors.append(get_color(agent))
    return xs, ys, colors


def terminate():
    global TERMINATING
    if TERMINATING:
        return

    TERMINATING = True
    curdoc().remove_periodic_callback(update_callback)


def update():
    engine.tick()

    s = slice(engine.agent_count)
    x, y, color = summarise(engine.agents)
    source.patch({
        'x': [(s, x)],
        'y': [(s, y)],
        'color': [(s, color)]
    })

    status_source.stream({
        "index": [engine.ticks],
        AgentStatus.DEAD.name: [engine.stats.get(AgentStatus.DEAD.name, 0)],
        AgentStatus.IMMUNE.name: [engine.stats.get(AgentStatus.IMMUNE.name, 0)],
        AgentStatus.INFECTIOUS.name: [engine.stats.get(AgentStatus.INFECTIOUS.name, 0)],
        AgentStatus.SUSCEPTIBLE.name: [engine.stats.get(AgentStatus.SUSCEPTIBLE.name, 0)],
    })

    if engine.stats.get(AgentStatus.INFECTIOUS.name, 0) == 0 and not TERMINATING:
        curdoc().add_timeout_callback(terminate, 8000)


def get_parameters():  # Get query parameters
    def cajole(value, minimum, maximum):
        return min(max(value, minimum), maximum)

    params = {}
    for key in DEFAULT_PARAMETERS:
        try:
            params[key] = cajole(float(
                curdoc().session_context.request.arguments.get(key)[0]),
                DEFAULT_PARAMETERS[key][0], DEFAULT_PARAMETERS[key][2])
        except:
            params[key] = DEFAULT_PARAMETERS[key][1]

    params['quarantining'] = params['quarantining'] == 1
    params['distancing_factor'] /= 100
    params['initial_immunity'] /= 100

    if not params['quarantining']:
        params['quarantine_delay'] = params['sickness_duration'] + 1

    return params


def make_engine(params):
    return Engine(n=int(params['agents']), SICKNESS_PROXIMITY=int(params['sickness_proximity']), SICKNESS_DURATION=int(
        params['sickness_duration']), DISTANCING_FACTOR=params['distancing_factor'], QUARANTINE_DELAY=int(params['quarantine_delay']), INITIAL_IMMUNITY=params['initial_immunity'])


# Create engine
params = get_parameters()
engine = make_engine(params)

data = {}
data['x'], data['y'], data['color'] = summarise(engine.agents)
source = ColumnDataSource(data)

p1 = figure(title="Epidemic Simulation", x_axis_label='x',
            y_axis_label='y', x_range=(0, MAX_X + QUARANTINE_X), y_range=(0, MAX_Y), tools="")
p1.scatter(x='x', y='y', color='color', line_width=2, source=source)
p1.line([MAX_X + 5, MAX_X + 5], [0, MAX_Y], line_width=2, color='#eeeeee')
p1.axis.visible = False
p1.xgrid.visible = False
p1.ygrid.visible = False

update_callback = curdoc().add_periodic_callback(update, 1000 // TICKS_PER_SECOND)

# Status Graph
names = [status.name for status in AgentStatus][::-1]
status_source = ColumnDataSource(pd.DataFrame(
    np.zeros((1, len(names))), columns=names))


def get_population_health_graph(names, params):
    p = figure(title="Population Health",
               x_range=DataRange1d(start=0, bounds=(0, None)),
               y_range=(0, params['agents']), tools="")
    p.grid.minor_grid_line_color = '#eeeeee'
    p.varea_stack(stackers=names, x='index',
                  color=('#718093', '#44bd32', '#e84118', '#00a8ff'), legend_label=names, source=status_source)
    p.legend.items.reverse()
    p.legend.click_policy = "hide"

    return p


p2 = get_population_health_graph(names, params)
controls = get_controls(params)

# About us
about_us = get_about_us()


# Plot to page
curdoc().add_root(
    gridplot([[p1, p2], [controls, about_us]], toolbar_location="left", toolbar_options={'logo': None}))
