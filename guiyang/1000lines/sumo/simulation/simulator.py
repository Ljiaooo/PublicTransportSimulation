import yaml
import json

from simulation.bus_controller import BusController
from simulation.passengerflow import PassengerFlow
from simulation import utils


class Simulator():
    '''
    Description:
        Customized simulation environment

    Args:
        line (string)
    '''

    def __init__(self, line, direction, date, startup_time=None) -> None:
        self.line = line
        
        # load timetable
        filename = 'data/{}/timetable/{}_{}_timetable.json'.format(line, date, direction)
        with open(filename, 'r') as f:
            self.timetable = json.load(f)
        self.timetable_index = 0

        if startup_time is None:
            startup_time = utils.str2seconds(self.timetable[0])
        
        self._t = startup_time
        self._startup_time = startup_time

        cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.Loader)
        self.cfg = cfg['simulation']

        self.bus_controller = BusController(self._startup_time, line, direction, date, self.cfg)
        self.passengerflow = PassengerFlow(self._startup_time, line, direction, date, self.cfg)
        self.bus_controller.set_passengerflow(self.passengerflow)

        self.headway = 0
        self.fleetsize_list = []
        self.log_interval = 60
        
        self._max_fleet_size = self.cfg['max_fleet_size']
        self._min_action = self.cfg['min_action']
        self._max_action = self.cfg['max_action']

    def step(self, step_size, log_fleetsize=False):
        if step_size < self._min_action:
            penalty = step_size - self._min_action
            step_size = self._min_action
        elif step_size > self._max_action:
            penalty = self._max_action - step_size
            step_size = self._max_action
        else:
            penalty = 0

        # if step_size <= 0:
        #     print('action must be a positive number')
        #     return {}, 0, False, {}
        
        if self._t > self.cfg['last_bus']:
            return {}, 0, True, {'discard': True}
        
        if log_fleetsize:
            self.fleetsize_list.clear()
            for _ in range(step_size):
                self.passengerflow.update()
                self.bus_controller.update()
                self._t += 1
                if self._t % self.log_interval == 0:
                    self.fleetsize_list.append(self.bus_controller.get_fleetsize())
        else:
            for _ in range(step_size):
                self.passengerflow.update()
                self.bus_controller.update()
            self._t += step_size
        self.bus_controller.dispatch()

        # get (obs, reward, done, info)
        fleetsize = self.bus_controller.get_fleetsize()
        t = self._t
        headway = self._get_headway()
        self.headway = headway
        traveltime = self.bus_controller.get_traveltime()
        distance = self.bus_controller.get_distance()
        onboard = self.bus_controller.get_onboard_number()

        if fleetsize < self._max_fleet_size:
            pad_size = self._max_fleet_size - fleetsize
            traveltime += [0] * pad_size
            distance += [0] * pad_size
            onboard += [0] * pad_size
        elif fleetsize > self._max_fleet_size:
            # print('fleetsize greater than max_fleet_size')
            traveltime = traveltime[0:self._max_fleet_size]
            distance = distance[0:self._max_fleet_size]
            onboard = onboard[0:self._max_fleet_size]
        obs = {'fleetsize': fleetsize, 't': t, 'headway': headway, 'traveltime': traveltime, 'distance': distance, 'onboard': onboard}

        # waiting_number = self.passengerflow.get_waiting_number()
        self.waiting_time = self.passengerflow.get_waiting_time(accumulate=False)
        self.passengerflow.reset_waiting_time()
        r1 = -100
        # r2 = -0.00142831 * self.waiting_time
        r2 = -0.00133 * self.waiting_time
        reward = (penalty + r1 + r2) / 100
        done = False
        info = {}

        if self._t > self.cfg['last_bus']:
            done = True
        return obs, reward, done, info

    def reset(self):
        '''
        Dispatch the first bus. Return obs
        '''
        self._t = self._startup_time
        self.passengerflow.reset()
        self.bus_controller.reset()
        self.bus_controller.dispatch()

        t = self._t
        headway = self._get_headway()
        self.headway = headway
        traveltime = [0] * self._max_fleet_size
        distance = [0] * self._max_fleet_size
        onboard = [0] * self._max_fleet_size
        obs = {'fleetsize': 1, 't': t, 'headway': headway, 'traveltime': traveltime, 'distance': distance, 'onboard': onboard}

        self.waiting_time = self.passengerflow.get_waiting_time(accumulate=False)
        self.passengerflow.reset_waiting_time()
        return obs

    def update(self):
        self.passengerflow.update()
        self.bus_controller.update()
        self._t += 1

    def manual_step(self):
        '''
        TODO: Missing penalty item in reward function
        '''
        fleetsize = self.bus_controller.get_fleetsize()
        t = self._t
        headway = self._get_headway()
        self.headway = headway
        traveltime = self.bus_controller.get_traveltime()
        distance = self.bus_controller.get_distance()
        onboard = self.bus_controller.get_onboard_number()

        if fleetsize < self._max_fleet_size:
            pad_size = self._max_fleet_size - fleetsize
            traveltime += [0] * pad_size
            distance += [0] * pad_size
            onboard += [0] * pad_size
        elif fleetsize > self._max_fleet_size:
            # print('fleetsize greater than max_fleet_size')
            traveltime = traveltime[0:self._max_fleet_size]
            distance = distance[0:self._max_fleet_size]
            onboard = onboard[0:self._max_fleet_size]
        obs = {'fleetsize': fleetsize, 't': t, 'headway': headway, 'traveltime': traveltime, 'distance': distance, 'onboard': onboard}

        self.waiting_time = self.passengerflow.get_waiting_time(accumulate=False)
        self.passengerflow.reset_waiting_time()
        r1 = -100
        # r2 = -0.00142831 * self.waiting_time
        r2 = -0.00133 * self.waiting_time
        reward = (r1 + r2) / 100
        done = False
        info = {}

        if self._t > self.cfg['last_bus']:
            done = True
        return obs, reward, done, info
        
    def get_headway(self) -> int:
        return self.headway

    def get_timestamp(self) -> int:
        return self._t

    def get_fleetsize_log(self) -> list:
        return self.fleetsize_list.copy()

    def get_waiting_time_log(self) -> int:
        return self.waiting_time
    
    def _get_headway(self):
        while True:
            if self.timetable_index == len(self.timetable):
                return self.cfg['default_headway']

            t2 = utils.str2seconds(self.timetable[self.timetable_index])
            if self._t > t2:
                self.timetable_index += 1
            else:
                if self.timetable_index == 0:
                    return self.cfg['default_headway']
                else:
                    t1 = utils.str2seconds(self.timetable[self.timetable_index - 1])
                    return t2 - t1
        