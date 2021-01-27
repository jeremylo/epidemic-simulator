from .simulator import TICKS_PER_SECOND
from bokeh.layouts import column
from bokeh.models import Slider, Toggle, Div, CustomJS


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
