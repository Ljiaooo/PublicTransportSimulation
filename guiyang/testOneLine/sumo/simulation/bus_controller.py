import json
import traci

from simulation import utils


class BusController:
    '''
    control the status of all buses on the route

    data format: data[bus_index]
    '''

    def __init__(self, startup_time, line, direction, date,sumoController) -> None:
        self._t = startup_time
        self._startup_time = startup_time
        self._passengerflow = None

        self.fleetsize = 0
        self.traveltime = []
        self.distance = []
        self.onboard = []
        # self.dwelltime = []

        self._speed = []  # current speed
        self._arrivaltime = []  # estimated arrival time
        self._traveltime = []  # estimated travel time
        self._onboard = []  # last section onboard passenger
        self._station = []  # last station

        self._speed_data = {}  # historical data
        self._speed_data_index = {}  # fast search
        self._distance_data = {}  # historical data

        self._to_del = []
        
        self.line =line
        self.t_index = 0
        self.direction = 0 if direction == 'up' else 1

        #self._board_speed = cfg['board_speed']

        self.sumo_controller = sumoController

        filename = 'sumo/data/res/{}_id2name.json'.format(line)
        with open(filename, 'r',encoding='utf-8') as f:
            self._id2name_dict = json.load(f)[direction]

        filename = 'sumo/data/res/{}_name2id.json'.format(line)
        with open(filename, 'r',encoding='utf-8') as f:
            self._name2id_dict = json.load(f)[direction]
        station_list = list(self._name2id_dict.keys())
        self._starting_station = station_list[0]
        self._terminus = station_list[-1]
        for k, _ in self._name2id_dict.items():
            self._speed_data_index[k] = 0

        # load speed data
        filename = 'sumo/data/{}/speed/{}_{}_speed.json'.format(line, date, direction)
        with open(filename, 'r',encoding='utf-8') as f:
            self._speed_data = json.load(f)

        # load distance data
        filename = 'sumo/data/distance/{}_{}_distance.json'.format(line, direction)
        with open(filename, 'r',encoding='utf-8') as f:
            self._distance_data = json.load(f)

        with open("sumo/data/{}/timetable/0000_{}_timetable.json".format(line, direction),'r',encoding='utf-8') as f:
            self.timetable = json.load(f)

    def sumo_update(self):
        '''
        update all state
        '''
        self._t += 1

        arrived = list(traci.simulation.getArrivedIDList())
        #busOnTheRoad = self.sumo_controller.busOnTheUpRoad if self.direction == 0 else self.sumo_controller.busOnTheDownRoad
        busOnTheRoad = self.sumo_controller.busOnTheRoad
        busOnTheRoad = [bus for bus in self.busOnTheRoad if bus[4]==str(self.direction)]
        for i,bus in enumerate(arrived+busOnTheRoad):

            if i==0 and arrived:
                last_station = self._station[i]
                station_id = self._name2id_dict[last_station]
                station = self._id2name_dict[str(station_id + 1)]

                # debug
                # tmp_t = utils.seconds2str(self._t)
                # print('speed:{:6f}\ttime:{}\tstation:{}'.format(self._speed[i], tmp_t, station))

                if station == self._terminus:
                    # arrive at the terminus
                    self._to_del.append(i)
                    self._passengerflow.board(station, self._onboard[i])
                    self._passengerflow.alight(station)
                    print('arrived!')
            elif traci.vehicle.isAtBusStop(bus) and traci.vehicle.getSpeed(bus)==0 and traci.vehicle.getAcceleration(bus)!=0:

                if not self._station[i]:
                    self._station[i] = self._starting_station
                    continue
                    
                    
                # arrive at the next station
                last_station = self._station[i]
                station_id = self._name2id_dict[last_station]
                station = self._id2name_dict[str(station_id + 1)]

                # debug
                # tmp_t = utils.seconds2str(self._t)
                # print('speed:{:6f}\ttime:{}\tstation:{}'.format(self._speed[i], tmp_t, station))

                if station == self._terminus:
                    # arrive at the terminus
                    self._to_del.append(i)
                    self._passengerflow.board(station, self._onboard[i])
                    self._passengerflow.alight(station)
                    print('arrived!')
                    continue

                self.traveltime[i] = self._traveltime[i]
                self.distance[i] = self._distance_data[last_station]
                self.onboard[i] = self._onboard[i]

                self._station[i] = station

                board = self._passengerflow.board(station, self._onboard[i])
                alight = self._passengerflow.alight(station)
                if self._onboard[i] >= alight:
                    self._onboard[i] += board - alight
                else:
                    self._onboard[i] = board

                self._update_speed(station, i)

                s = self._distance_data[station]
                v = self._speed[i]
                traveltime = int(s / v)
                self._traveltime[i] = traveltime

                # num_people = board if board > alight else alight
                # dwelltime = int(num_people * self._board_speed)
                # self._arrivaltime[i] = self._t + traveltime + dwelltime
                self._arrivaltime[i] = self._t + traveltime

                #下车
                passengerOnBus = traci.vehicle.getPersonIDList(bus)
                if len(passengerOnBus)>=alight:
                    for passenger in passengerOnBus[:alight]:
                        traci.person.removeStages(passenger)
                else:
                    for passenger in passengerOnBus:
                        traci.person.removeStages(passenger)

                #更改车辆速度
                traci.vehicle.setSpeed(bus, self._speed[i])


        for i in reversed(self._to_del):
            self.fleetsize -= 1
            self.traveltime.pop(i)
            self.distance.pop(i)
            self.onboard.pop(i)
            self._speed.pop(i)
            self._arrivaltime.pop(i)
            self._traveltime.pop(i)
            self._onboard.pop(i)
            self._station.pop(i)

        self._to_del.clear()

        if self.t_index < len(self.timetable):
            time = self.timetable[self.t_index]
            if self._t == utils.str2seconds(time):
                self.dispatch()
                self.sumo_controller.addBus(self.direction)
                self.t_index += 1

    def update(self):
        '''
        update all state
        '''
        self._t += 1
        for i in range(self.fleetsize):
            if self._t >= self._arrivaltime[i]:
                # arrive at the next station
                last_station = self._station[i]
                station_id = self._name2id_dict[last_station]
                station = self._id2name_dict[str(station_id + 1)]

                # debug
                # tmp_t = utils.seconds2str(self._t)
                # print('speed:{:6f}\ttime:{}\tstation:{}'.format(self._speed[i], tmp_t, station))

                if station == self._terminus:
                    # arrive at the terminus
                    self._to_del.append(i)
                    self._passengerflow.board(station, self._onboard[i])
                    self._passengerflow.alight(station)
                    continue

                self.traveltime[i] = self._traveltime[i]
                self.distance[i] = self._distance_data[last_station]
                self.onboard[i] = self._onboard[i]

                self._station[i] = station

                board = self._passengerflow.board(station, self._onboard[i])
                alight = self._passengerflow.alight(station)
                if self._onboard[i] >= alight:
                    self._onboard[i] += board - alight
                else:
                    self._onboard[i] = board

                self._update_speed(station, i)

                s = self._distance_data[station]
                v = self._speed[i]
                traveltime = int(s / v)
                self._traveltime[i] = traveltime

                # num_people = board if board > alight else alight
                # dwelltime = int(num_people * self._board_speed)
                # self._arrivaltime[i] = self._t + traveltime + dwelltime
                self._arrivaltime[i] = self._t + traveltime

        for i in reversed(self._to_del):
            self.fleetsize -= 1
            self.traveltime.pop(i)
            self.distance.pop(i)
            self.onboard.pop(i)
            self._speed.pop(i)
            self._arrivaltime.pop(i)
            self._traveltime.pop(i)
            self._onboard.pop(i)
            self._station.pop(i)

        self._to_del.clear()

    def get_traveltime(self):
        return self.traveltime.copy()

    def get_distance(self):
        return self.distance.copy()

    def get_onboard_number(self):
        return self.onboard.copy()

    def get_fleetsize(self):
        return self.fleetsize

    def set_passengerflow(self, passengerflow):
        self._passengerflow = passengerflow

    def dispatch(self):
        self.fleetsize += 1
        self.traveltime.append(0)
        self.distance.append(0)
        self.onboard.append(0)

        #self._station.append(self._starting_station)
        self._station.append('')

        # look up table, update _speed table
        self._speed.append(0)
        self._update_speed(self._starting_station, -1)

        s = self._distance_data[self._starting_station]
        v = self._speed[-1]
        traveltime = int(s / v)
        self._traveltime.append(traveltime)

        board = self._passengerflow.board(self._starting_station)
        self._onboard.append(board)
        # dwelltime = int(board * self._board_speed)
        # self._arrivaltime.append(self._t + traveltime + dwelltime)
        self._arrivaltime.append(self._t + traveltime)

    def reset(self):
        self._t = self._startup_time
        self.fleetsize = 0
        self.traveltime.clear()
        self.distance.clear()
        self.onboard.clear()
        self._speed.clear()
        self._arrivaltime.clear()
        self._traveltime.clear()
        self._onboard.clear()
        self._station.clear()
        for k, _ in self._speed_data_index.items():
            self._speed_data_index[k] = 0

    def _update_speed(self, station, bus_index):
        speed_data = self._speed_data[station]
        departuretime = speed_data['departure_time']
        speed = speed_data['speed']
        arrivaltime = speed_data['arrival_time']

        while True:
            index = self._speed_data_index[station]
            if index == len(speed):
                self._speed[bus_index] = speed[index - 1]
                break

            depar_t = utils.str2seconds(departuretime[index])
            if self._t <= depar_t:
                if index == 0:
                    self._speed[bus_index] = speed[index]
                    break
                else:
                    v1 = speed[index - 1]
                    v2 = speed[index]
                    t1 = arrivaltime[index - 1]
                    t1 = utils.str2seconds(t1)
                    t2 = departuretime[index]
                    t2 = utils.str2seconds(t2)
                    beta = (self._t - t1) / (t2 - t1)
                    v = v1 * (1 - beta) + v2 * beta
                    self._speed[bus_index] = v
                    break
            else:
                arri_t = utils.str2seconds(arrivaltime[index])
                if self._t <= arri_t:
                    # hit
                    self._speed[bus_index] = speed[index]
                    break
                else:
                    self._speed_data_index[station] += 1

    # def _update_speed(self, station):
    #     speed_data = self._speed_data[station]
    #     departuretime = speed_data['departure_time']
    #     speed = speed_data['speed']
    #     arrivaltime = speed_data['arrival_time']

    #     # binary search
    #     i = 0
    #     j = len(speed) - 1
    #     while True:
    #         mid = (i + j) // 2
    #         depar_t = utils.str2seconds(departuretime[mid])
    #         if self._t >= depar_t:
    #             arri_t = utils.str2seconds(arrivaltime[i])
    #             if self._t <= arri_t:
    #                 # hit
    #                 self._speed.append(speed[mid])
    #                 break
    #             else:
    #                 # continue searching
    #                 i = mid + 1
    #         else:
    #             j = mid - 1

    #         if i == j:
    #             depar_t = utils.str2seconds(departuretime[i])
    #             arri_t = utils.str2seconds(arrivaltime[i])
    #             if self._t < depar_t:
    #                 if i != 0:
    #                     speed1 = speed[i - 1]
    #                     speed2 = speed[i]
    #                     pre_arri_t = utils.str2seconds(arrivaltime[i - 1])
    #                     beta = (self._t - pre_arri_t) / (depar_t - pre_arri_t)
    #                     cur_speed = speed1 * (1 - beta) + speed2 * beta
    #                     self._speed.append(cur_speed)
    #                     break
    #                 else:
    #                     self._speed.append(speed[0])
    #                     break
    #             elif self._t < arri_t:
    #                 self._speed.append(speed[i])
    #                 break
    #             else:
    #                 if i != len(speed) - 1:
    #                     speed1 = speed[i]
    #                     speed2 = speed[i + 1]
    #                     next_depar_t = utils.str2seconds(departuretime[i + 1])
    #                     beta = (self._t - arri_t) / (next_depar_t - arri_t)
    #                     cur_speed = speed1 * (1 - beta) + speed2 * beta
    #                     self._speed.append(cur_speed)
    #                     break
