import os
import json

from simulation.simulator import Simulator
from simulation.utils import str2seconds, seconds2str

class SimController:
    def __init__(self):
        line = '_111'
        direction = 'up'
        startup_time = str2seconds('06:30:00')

        # 1000 lines
        self.simulators = []
        self.timetables = []
        self.timetable_index = []

        simulator = Simulator(line, direction, '0000', startup_time=startup_time)
        simulator.reset()
        self.simulators.append(simulator)

        with open('./testOneLine/sumo/data/{}/0000_{}_timetable.json'.format(line, direction), 'r') as f:
            timetable = json.load(f)
            timetable = list(map(str2seconds, timetable))
            self.timetables.append(timetable)
            self.timetable_index.append(0)

    def update(self):
        for i in range(len(self.simulators)):
            simulator = self.simulators[i]
            timetable = self.timetables[i]
            simulator.update()
            t_index = self.timetable_index[i]
            if t_index < len(timetable) and simulator._t >= timetable[t_index]:
                # departure
                simulator.bus_controller.dispatch()
                self.timetable_index[i] += 1


