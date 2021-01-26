import numpy as np
import pandas as pd

from bokeh.layouts import gridplot
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.colors import RGB
from bokeh.models import DataRange1d, Slider, Toggle, Div, CustomJS

from .simulator import Engine, AgentStatus, MAX_X, MAX_Y, QUARANTINE_X

TICKS_PER_SECOND = 20
TO_BE_TERMINATED = False


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


def terminate():
    global TO_BE_TERMINATED
    if TO_BE_TERMINATED:
        return

    TO_BE_TERMINATED = True
    curdoc().remove_periodic_callback(update_callback)


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

    if engine.stats.get(AgentStatus.INFECTIOUS.name, 0) == 0 and not TO_BE_TERMINATED:
        curdoc().add_timeout_callback(terminate, 8000)


def add_control(control, query_param):
    control.js_on_change('value', CustomJS(code="""
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set("{query_param}", cb_obj.value);
    window.location.search = searchParams.toString();
    """.format(query_param=query_param)))
    return control


# Get query parameters/set default parameters
PARAMS = {}
for key, default in [('agents', 200), ('sickness_proximity', 15), ('sickness_duration', 12.5), ('quarantine_delay', 5), ('distancing_factor', 0.5), ('quarantining', 0)]:
    try:
        PARAMS[key] = float(
            curdoc().session_context.request.arguments.get(key)[0])
    except:
        PARAMS[key] = default

# Scale any parameters as required
PARAMS['sickness_duration'] = PARAMS['sickness_duration'] * TICKS_PER_SECOND
PARAMS['quarantine_delay'] = PARAMS['quarantine_delay'] * TICKS_PER_SECOND
PARAMS['distancing_factor'] = PARAMS['distancing_factor'] / 1000
PARAMS['quarantining'] = True if PARAMS['quarantining'] == 1 else False

if PARAMS['quarantining']:
    PARAMS['quarantine_delay'] = PARAMS['sickness_duration'] + 100

# Create engine
engine = Engine(n=int(PARAMS['agents']), SICKNESS_PROXIMITY=int(PARAMS['sickness_proximity']), SICKNESS_DURATION=int(
    PARAMS['sickness_duration']), DISTANCING_FACTOR=PARAMS['distancing_factor'], QUARANTINE_DELAY=int(PARAMS['quarantine_delay']))

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

update_callback = curdoc().add_periodic_callback(update, 50)

# Status Graph
names = [AgentStatus.DEAD.name, AgentStatus.IMMUNE.name,
         AgentStatus.INFECTIOUS.name, AgentStatus.SUSCEPTIBLE.name]

status_source = ColumnDataSource(pd.DataFrame(np.zeros((1, 4)), columns=names))

p2 = figure(title="Population Health",
            x_range=DataRange1d(start=0, bounds=(0, None)),
            y_range=(0, PARAMS['agents']), tools="")
p2.grid.minor_grid_line_color = '#eeeeee'
p2.varea_stack(stackers=names, x='index',
               color=('#718093', '#44bd32', '#e84118', '#00a8ff'), legend_label=names, source=status_source)
p2.legend.items.reverse()
p2.legend.click_policy = "hide"

# Add controls
c1 = add_control(Slider(start=1, end=500, value=PARAMS['agents'],
                        step=1, title="Number of agents"), "agents")

c2 = add_control(Slider(start=1, end=30, value=PARAMS['sickness_proximity'],
                        step=1, title="Sickness proximity"), "sickness_proximity")

c3 = add_control(Slider(start=1, end=300, value=PARAMS['sickness_duration'] / TICKS_PER_SECOND,
                        step=0.5, title="Sickness duration (seconds)"), "sickness_duration")

c4 = add_control(Slider(start=1, end=300, value=PARAMS['quarantine_delay'] / TICKS_PER_SECOND,
                        step=0.5, title="Quarantine delay (seconds)"), "quarantine_delay")

c5 = add_control(Slider(start=1, end=100, value=PARAMS['distancing_factor'] * 1000,
                        step=0.5, title="Distancing factor (percentage)"), "distancing_factor")

toggle = Toggle(label="Quarantine enabled" if PARAMS['quarantining'] else "Quarantine disabled",
                button_type="success" if PARAMS['quarantining'] else "danger", active=PARAMS['quarantining'])
toggle.js_on_click(CustomJS(code="""
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set("quarantining", this.active ? 1 : 0);
    window.location.search = searchParams.toString();
"""))

controls = gridplot([[c1], [c2], [c3], [c4], [c5], [
                    toggle]], toolbar_location="left", toolbar_options={'logo': None})

# About us
div = Div(text="""
Our epidemic simulator lets you track the progression of a localised disease outbreak according to various configurable parameters.
<br><br>
This project was developed by <a href="https://github.com/jeremylo">Jeremy Lo Ying Ping</a> and <a href="https://github.com/shu8">Shubham Jain</a>, initially as part of the <a href="https://devpost.com/software/epidemic-simulator-wz83sm" target="_blank" rel="noopener noreferer">Hex Cambridge 2021</a> hackathon.
<br><br>
The code is fully open source and available on GitHub at <a href="https://github.com/jeremylo/epidemic-simulator" target="_blank" rel="noopener noreferer">https://github.com/jeremylo/epidemic-simulator</a>.
""", style={'fontSize': '1.2em'})


# Plot to page
curdoc().add_root(
    gridplot([[p1, p2], [controls, div]], toolbar_location="left", toolbar_options={'logo': None}))
