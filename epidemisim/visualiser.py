from .simulator import AgentStatus, MAX_X, MAX_Y, QUARANTINE_X, TICKS_PER_SECOND
from bokeh.colors import RGB
from bokeh.layouts import column
from bokeh.models import DataRange1d, Slider, Toggle, Div, CustomJS
from bokeh.plotting import figure


def get_color(agent):
    if agent.status == AgentStatus.DEAD:
        return RGB(113, 128, 147).lighten(agent.frailty).to_css()  # 718093
    elif agent.status == AgentStatus.IMMUNE:
        return RGB(68, 189, 50).lighten(agent.frailty).to_css()  # 44bd32
    elif agent.status == AgentStatus.INFECTIOUS:
        return RGB(232, 65, 24).lighten(agent.frailty).to_css()  # e84118
    elif agent.status == AgentStatus.SUSCEPTIBLE:
        return RGB(0, 168, 255).lighten(agent.frailty).to_css()  # 00a8ff

########################################
# IMPORTANT GRAPHS                     #
########################################


def get_visualisation(visualisation_source):
    p = figure(title="Epidemic Simulation", x_axis_label='x',
               y_axis_label='y', x_range=(0, MAX_X + QUARANTINE_X), y_range=(0, MAX_Y), tools="")
    p.scatter(x='x', y='y', color='color',
              line_width=2, source=visualisation_source)
    p.line([MAX_X + 5, MAX_X + 5], [0, MAX_Y], line_width=2, color='#eeeeee')
    p.axis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False

    return p


def get_population_health_graph(names, status_source, agent_count: int):
    p = figure(title="Population Health",
               x_range=DataRange1d(start=0, bounds=(0, None)),
               y_range=(0, agent_count), tools="")
    p.grid.minor_grid_line_color = '#eeeeee'
    p.varea_stack(stackers=names, x='index',
                  color=('#718093', '#44bd32', '#e84118', '#00a8ff'), legend_label=names, source=status_source)
    p.legend.items.reverse()
    p.legend.click_policy = "hide"

    return p


##################
# CONTROLS       #
##################


def add_control(control, query_param):
    control.js_on_change('value', CustomJS(code="""
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set("{query_param}", cb_obj.value);
    window.location.search = searchParams.toString();
    """.format(query_param=query_param)))
    return control


def get_simulation_controls(params):
    return [
        Div(text="""<strong>Simulation Controls</strong>"""),
        add_control(Slider(start=1, end=500, value=params['agents'],
                           step=1, title="Number of agents"), "agents"),
        add_control(Slider(start=0, end=100, value=params['initial_immunity'] * 100,
                           step=1, title="Initial immunity (%)"), "initial_immunity")
    ]


def get_disease_controls(params):
    return [
        Div(text="""<strong>Disease Profile Controls</strong>"""),
        add_control(Slider(start=1, end=30, value=params['sickness_proximity'],
                           step=1, title="Sickness proximity"), "sickness_proximity"),
        add_control(Slider(start=1, end=500, value=params['sickness_duration'],
                           step=1, title="Sickness duration (ticks)"), "sickness_duration")
    ]


def get_response_controls(params):
    toggle = Toggle(label="Quarantine enabled" if params['quarantining'] else "Quarantine disabled",
                    button_type="success" if params['quarantining'] else "danger", active=params['quarantining'])
    toggle.js_on_click(CustomJS(code="""
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set("quarantining", this.active ? 1 : 0);
    window.location.search = searchParams.toString();
"""))
    return [
        Div(text="""<strong>Disease Response Controls</strong>"""),
        add_control(Slider(start=1, end=500, value=params['quarantine_delay'],
                           step=1, title="Quarantine delay (ticks)"), "quarantine_delay"),
        add_control(Slider(start=0, end=100, value=params['distancing_factor'] * 100,
                           step=0.1, title="Distancing factor (%)"), "distancing_factor"),
        toggle
    ]


def get_controls(params):
    return column(*get_simulation_controls(params), *
                  get_disease_controls(params), *get_response_controls(params))

###############
# ABOUT US    #
###############


def get_about_us():
    return Div(text="""
Our epidemic simulator lets you track the progression of a simplified model of a localised disease outbreak according to various configurable parameters.
<br><br>
This project was developed by <a href="https://github.com/jeremylo">Jeremy Lo Ying Ping</a> and <a href="https://github.com/shu8">Shubham Jain</a>, initially as part of the <a href="https://devpost.com/software/epidemic-simulator-wz83sm" target="_blank" rel="noopener noreferer">Hex Cambridge 2021</a> hackathon.
<br><br>
The code is fully open source and available on GitHub at <a href="https://github.com/jeremylo/epidemic-simulator" target="_blank" rel="noopener noreferer">https://github.com/jeremylo/epidemic-simulator</a>.
<br><br>
The simulator engine is currently running at {0} ticks per second.
""".format(TICKS_PER_SECOND), style={'fontSize': '1.2em'})
