import numpy as np
import pandas as pd

from bokeh.layouts import gridplot
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import curdoc
from bokeh.models import ColumnDataSource

from .simulator import Engine, AgentStatus, TICKS_PER_SECOND
from .visualiser import get_about_us, get_controls, get_color, get_population_health_graph, get_visualisation

PARAMETERS = {  # MINIMUM, DEFAULT, MAXIMUM
    'agents': (1, 200, 500),
    'initial_immunity': (0, 0, 100),

    'sickness_proximity': (1, 15, 30),
    'sickness_duration': (1, 250, 500),

    'quarantine_delay': (0, 249, 501),
    'distancing_factor': (0, 1, 100),
    'quarantining': (0, 0, 1)
}


class Controller:
    terminating = False

    def __init__(self, params) -> None:
        self.params = params
        self.engine = self.make_engine(params)

        data = {}
        data['x'], data['y'], data['color'] = self.summarise(
            self.engine.agents)
        self.visualisation_source = ColumnDataSource(data)

        self.names = [status.name for status in AgentStatus][::-1]
        self.status_source = ColumnDataSource(pd.DataFrame(
            np.zeros((1, len(self.names))), columns=self.names))

        self.start()

    def summarise(self, agents):
        xs, ys, colors = [], [], []
        for agent in agents:
            xs.append(agent.position[0])
            ys.append(agent.position[1])
            colors.append(get_color(agent))
        return xs, ys, colors

    def make_engine(self, params) -> Engine:
        return Engine(n=int(params['agents']), SICKNESS_PROXIMITY=int(params['sickness_proximity']),
                      SICKNESS_DURATION=int(params['sickness_duration']), DISTANCING_FACTOR=params['distancing_factor'],
                      QUARANTINE_DELAY=int(params['quarantine_delay']), INITIAL_IMMUNITY=params['initial_immunity'])

    def show(self) -> None:
        curdoc().add_root(gridplot([
            [
                get_visualisation(self.visualisation_source),
                get_population_health_graph(
                    self.names, self.status_source, params['agents'])
            ],
            [get_controls(params), get_about_us()]
        ], toolbar_location="left", toolbar_options={'logo': None}))

    def start(self) -> None:
        self.update_callback = curdoc().add_periodic_callback(
            self.update, 1000 // TICKS_PER_SECOND)

    def update(self) -> None:
        self.engine.tick()

        s = slice(self.engine.agent_count)
        x, y, color = self.summarise(self.engine.agents)
        self.visualisation_source.patch({
            'x': [(s, x)],
            'y': [(s, y)],
            'color': [(s, color)]
        })

        self.status_source.stream({
            "index": [self.engine.ticks],
            AgentStatus.DEAD.name: [self.engine.stats.get(AgentStatus.DEAD.name, 0)],
            AgentStatus.IMMUNE.name: [self.engine.stats.get(AgentStatus.IMMUNE.name, 0)],
            AgentStatus.INFECTIOUS.name: [self.engine.stats.get(AgentStatus.INFECTIOUS.name, 0)],
            AgentStatus.SUSCEPTIBLE.name: [self.engine.stats.get(AgentStatus.SUSCEPTIBLE.name, 0)],
        })

        if self.engine.stats.get(AgentStatus.INFECTIOUS.name, 0) == 0 and not self.terminating:
            curdoc().add_timeout_callback(self.terminate, 8000)

    def terminate(self) -> None:
        if self.terminating:
            return

        self.terminating = True
        curdoc().remove_periodic_callback(self.update_callback)

    def reset(self) -> None:
        self.terminate()
        self.status_source.data = {
            "index": [],
            AgentStatus.DEAD.name: [],
            AgentStatus.IMMUNE.name: [],
            AgentStatus.INFECTIOUS.name: [],
            AgentStatus.SUSCEPTIBLE.name: [],
        }
        self.engine = self.make_engine(self.params)
        self.terminating = False
        self.start()


def get_parameters():  # Get query parameters
    def cajole(value, minimum, maximum):
        return min(max(value, minimum), maximum)

    params = {}
    for key in PARAMETERS:
        try:
            params[key] = cajole(float(
                curdoc().session_context.request.arguments.get(key)[0]),
                PARAMETERS[key][0], PARAMETERS[key][2])
        except:
            params[key] = PARAMETERS[key][1]

    params['quarantining'] = params['quarantining'] == 1
    params['distancing_factor'] /= 100
    params['initial_immunity'] /= 100

    if not params['quarantining']:
        params['quarantine_delay'] = params['sickness_duration'] + 1

    return params


# Create engine
params = get_parameters()
controller = Controller(params)
controller.show()
