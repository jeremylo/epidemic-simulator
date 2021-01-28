from .simulator import MAX_X, MAX_Y, QUARANTINE_X, TICKS_PER_SECOND, PARAMETERS
from bokeh.layouts import column
from bokeh.models import DataRange1d, Slider, Toggle, Div
from bokeh.plotting import figure


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
               y_range=DataRange1d(start=0, bounds=(0, None)), tools="")
    p.grid.minor_grid_line_color = '#eeeeee'
    p.varea_stack(stackers=names, x='index',
                  color=('#718093', '#44bd32', '#e84118', '#00a8ff'), legend_label=names, source=status_source)
    p.legend.items.reverse()
    p.legend.click_policy = "hide"

    return p


##################
# CONTROLS       #
##################


def wrap(control: Slider, controller, key: str):
    def update_controller(attr, old, new):
        controller.update_parameter(key, new)
        controller.reset()

    control.on_change('value_throttled', update_controller)

    return control


def get_simulation_controls(controller):
    return [
        Div(text="""<strong>Simulation Controls</strong>"""),
        wrap(Slider(start=PARAMETERS['agents'][0], end=PARAMETERS['agents'][2], value=controller.params['agents'],
                    step=1, title="Number of agents"), controller, 'agents'),
        wrap(Slider(start=PARAMETERS['initial_immunity'][0], end=PARAMETERS['initial_immunity'][2], value=controller.params['initial_immunity'] * 100,
                    step=1, title="Initial immunity (%)"), controller, 'initial_immunity')
    ]


def get_disease_controls(controller):
    return [
        Div(text="""<strong>Disease Profile Controls</strong>"""),
        wrap(Slider(start=PARAMETERS['sickness_proximity'][0], end=PARAMETERS['sickness_proximity'][2], value=controller.params['sickness_proximity'],
                    step=1, title="Sickness proximity"), controller, "sickness_proximity"),
        wrap(Slider(start=PARAMETERS['sickness_duration'][0], end=PARAMETERS['sickness_duration'][2], value=controller.params['sickness_duration'],
                    step=1, title="Sickness duration (ticks)"), controller, "sickness_duration")
    ]


def get_response_controls(controller):

    toggle = Toggle(label="Quarantine enabled" if controller.params['quarantining'] else "Quarantine disabled",
                    button_type="success" if controller.params['quarantining'] else "danger", active=controller.params['quarantining'])

    def toggle_callback(event):
        controller.update_parameter(
            'quarantining', not controller.params['quarantining'])

        if controller.params['quarantining']:
            toggle.label = "Quarantine enabled"
            toggle.button_type = "success"
        else:
            toggle.label = "Quarantine disabled"
            toggle.button_type = "danger"

        controller.reset()

    toggle.on_click(toggle_callback)

    return [
        Div(text="""<strong>Disease Response Controls</strong>"""),
        wrap(Slider(start=PARAMETERS['quarantine_delay'][0], end=PARAMETERS['quarantine_delay'][2], value=controller.params['quarantine_delay'],
                    step=1, title="Quarantine delay (ticks)"), controller, "quarantine_delay"),
        wrap(Slider(start=PARAMETERS['distancing_factor'][0], end=PARAMETERS['distancing_factor'][2], value=controller.params['distancing_factor'] * 100,
                    step=0.5, title="Distancing factor (%)"), controller, "distancing_factor"),
        toggle
    ]


def get_controls(controller):
    return column(*get_simulation_controls(controller), *
                  get_disease_controls(controller), *get_response_controls(controller))

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
