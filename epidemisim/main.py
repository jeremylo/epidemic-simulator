import numpy as np
import pandas as pd

from bokeh.layouts import gridplot
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import curdoc
from bokeh.models import ColumnDataSource

from .simulator import Engine, AgentStatus, TICKS_PER_SECOND, PARAMETERS
from .visualiser import get_about_us, get_controls, get_color, get_population_health_graph, get_visualisation


def cajole(value, minimum, maximum):
    return min(max(value, minimum), maximum)


class Controller:
    params = {}
    terminating = False

    def __init__(self, params={}) -> None:
        self.params = {param: PARAMETERS[param][1] for param in PARAMETERS}
        self.params['quarantining'] = self.params['quarantining'] == 1
        self.params['distancing_factor'] /= 100
        self.params['initial_immunity'] /= 100

        for param in params:
            self.update_parameter(param, params[param])

        self.engine = self.make_engine()

        data = {}
        data['x'], data['y'], data['color'] = self.summarise(
            self.engine.agents)
        self.visualisation_source = ColumnDataSource(data)

        self.names = [status.name for status in AgentStatus][::-1]
        self.status_source = ColumnDataSource(pd.DataFrame(
            np.zeros((1, len(self.names))), columns=self.names))

        self.start()

    def update_parameter(self, key, value):
        try:
            self.params[key] = cajole(
                float(value), PARAMETERS[key][0], PARAMETERS[key][2])
        except:
            self.params[key] = PARAMETERS[key][1]

        if key in ('agents', 'sickness_proximity', 'sickness_duration', 'quarantine_delay'):
            self.params[key] == int(self.params[key])
        elif key == 'initial_immunity':
            self.params[key] /= 100
        elif key == 'distancing_factor':
            self.params['distancing_factor'] /= 100
        elif key == 'quarantining':
            self.params['quarantining'] = self.params['quarantining'] == 1

        if not self.params['quarantining']:
            self.params['quarantine_delay'] = self.params['sickness_duration'] + 1

    def summarise(self, agents):
        xs, ys, colors = [], [], []
        for agent in agents:
            xs.append(agent.position[0])
            ys.append(agent.position[1])
            colors.append(get_color(agent))
        return xs, ys, colors

    def make_engine(self) -> Engine:
        return Engine(n=int(self.params['agents']), SICKNESS_PROXIMITY=int(self.params['sickness_proximity']),
                      SICKNESS_DURATION=int(self.params['sickness_duration']), DISTANCING_FACTOR=self.params['distancing_factor'],
                      QUARANTINE_DELAY=int(self.params['quarantine_delay']), INITIAL_IMMUNITY=self.params['initial_immunity'])

    def show(self) -> None:
        self.visualisation = get_visualisation(self.visualisation_source)
        self.population_health_graph = get_population_health_graph(
            self.names, self.status_source, self.params['agents'])

        curdoc().add_root(gridplot([
            [self.visualisation, self.population_health_graph],
            [get_controls(self), get_about_us()]
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

        try:
            curdoc().remove_periodic_callback(self.update_callback)
        except ValueError:
            pass

    def reset(self) -> None:
        self.terminate()

        self.engine = self.make_engine()

        data = {}
        data['x'], data['y'], data['color'] = self.summarise(
            self.engine.agents)
        self.visualisation_source.data = data

        self.status_source.data = {
            "index": [],
            AgentStatus.DEAD.name: [],
            AgentStatus.IMMUNE.name: [],
            AgentStatus.INFECTIOUS.name: [],
            AgentStatus.SUSCEPTIBLE.name: [],
        }

        self.terminating = False

        curdoc().add_next_tick_callback(self.start)


# Run
controller = Controller()
controller.show()
