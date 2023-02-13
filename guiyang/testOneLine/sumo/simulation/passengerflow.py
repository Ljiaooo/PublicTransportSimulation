import json
import datetime

from simulation import utils


class PassengerFlow:
    '''
    contain number of passengers per station

    data format: data[stationname]
    '''

    def __init__(self, startup_time, line, direction, date,  sumoController) -> None:
        self._t = startup_time
        self._startup_time = startup_time

        self.total_waiting_time = 0
        self.total_waiting_number = 0
        self.waiting_time = 0
        self.wait_timestamp = 0

        self._raw_data = {}
        self._raw_data_index = {}  # for fast searching
        self._fine_grained_data = {}  # to save memory
        self._invalid_waiting_time = {}  # passengers have boarded the bus
        self._arrive_time = {}
        self._board_time = {}
        self.board_passenger = {}
        self.alight_passenger = {}
        # self.waiting_time = {}

        self._max_onboard = 80
        self.direction = 0 if direction == "up" else 1
        self.line = line

        self.sumo_controller = sumoController

        # load passengerflow data
        filename = 'sumo/data/{}/passengerflow/{}_{}_passengerflow.json'.format(
            line, date, direction
        )
        with open(filename, 'r',encoding='utf-8') as f:
            self._raw_data = json.load(f)

        self.reset()

    def sumo_update(self):
        '''
        look up raw data. update 'board', 'aight', 'waiting time', 'waiting number'
        '''
        self._t += 1

        for i,(station, data) in enumerate(self._raw_data.items()):
            # self.waiting_time[station] += self.board_passenger[station]
            # self.waiting_time[station] += self._get_waiting_time(station)

            board_timestamp = self._fine_grained_data[station]['board']
            alight_timestamp = self._fine_grained_data[station]['alight']
            if len(board_timestamp) > 0 and self._t == board_timestamp[-1]:
                busID = "{}_{}_{}".format(self.line[1:].zfill(3), self.direction, str(i).zfill(2))
                self.sumo_controller.addPassenger(busID)
                self.total_waiting_number += 1
                # self.board_passenger[station] += 1
                self._arrive_time[station].append(self._t)
                self._board_time[station].append(0)
                self._fine_grained_data[station]['board'].pop(-1)
            if len(alight_timestamp) > 0 and self._t == alight_timestamp[-1]:
                self.alight_passenger[station] += 1
                self._fine_grained_data[station]['alight'].pop(-1)

            time = data['time']
            board = data['board']
            alight = data['alight']
            index = self._raw_data_index[station]
            if index == len(time) - 1:
                continue

            # arrive at the next time segment
            # update _fine_grained_data
            t = utils.str2seconds(time[index])
            if self._t > t:
                index += 1
                t2 = time[index]
                t2 = utils.str2seconds(t2)

                board_num = board[index]
                if board_num == 0:
                    self._fine_grained_data[station]['board'] = []
                else:
                    self.update_fine_grained_data(board_num, t, t2, station, 'board')
                    # step = (t2 - t) // board_num
                    # time_stamp = [i for i in range(t2, t, -step)]
                    # if len(time_stamp) > board_num:
                    #     time_stamp = time_stamp[0:board_num]
                    # self._fine_grained_data[station]['board'] = time_stamp

                alight_num = alight[index]
                if alight_num == 0:
                    self._fine_grained_data[station]['alight'] = []
                else:
                    self.update_fine_grained_data(alight_num, t, t2, station, 'alight')
                    # step = (t2 - t) // alight_num
                    # time_stamp = [i for i in range(t2, t, -step)]
                    # if len(time_stamp) > alight_num:
                    #     time_stamp = time_stamp[0:alight_num]
                    # self._fine_grained_data[station]['alight'] = time_stamp

                self._raw_data_index[station] = index
    def update(self):
        '''
        look up raw data. update 'board', 'aight', 'waiting time', 'waiting number'
        '''
        self._t += 1

        for station, data in self._raw_data.items():
            # self.waiting_time[station] += self.board_passenger[station]
            # self.waiting_time[station] += self._get_waiting_time(station)

            board_timestamp = self._fine_grained_data[station]['board']
            alight_timestamp = self._fine_grained_data[station]['alight']
            if len(board_timestamp) > 0 and self._t == board_timestamp[-1]:
                self.total_waiting_number += 1
                # self.board_passenger[station] += 1
                self._arrive_time[station].append(self._t)
                self._board_time[station].append(0)
                self._fine_grained_data[station]['board'].pop(-1)
            if len(alight_timestamp) > 0 and self._t == alight_timestamp[-1]:
                self.alight_passenger[station] += 1
                self._fine_grained_data[station]['alight'].pop(-1)

            time = data['time']
            board = data['board']
            alight = data['alight']
            index = self._raw_data_index[station]
            if index == len(time) - 1:
                continue

            # arrive at the next time segment
            # update _fine_grained_data
            t = utils.str2seconds(time[index])
            if self._t > t:
                index += 1
                t2 = time[index]
                t2 = utils.str2seconds(t2)

                board_num = board[index]
                if board_num == 0:
                    self._fine_grained_data[station]['board'] = []
                else:
                    self.update_fine_grained_data(board_num, t, t2, station, 'board')
                    # step = (t2 - t) // board_num
                    # time_stamp = [i for i in range(t2, t, -step)]
                    # if len(time_stamp) > board_num:
                    #     time_stamp = time_stamp[0:board_num]
                    # self._fine_grained_data[station]['board'] = time_stamp

                alight_num = alight[index]
                if alight_num == 0:
                    self._fine_grained_data[station]['alight'] = []
                else:
                    self.update_fine_grained_data(alight_num, t, t2, station, 'alight')
                    # step = (t2 - t) // alight_num
                    # time_stamp = [i for i in range(t2, t, -step)]
                    # if len(time_stamp) > alight_num:
                    #     time_stamp = time_stamp[0:alight_num]
                    # self._fine_grained_data[station]['alight'] = time_stamp

                self._raw_data_index[station] = index

    def get_waiting_time(self, accumulate=True) -> int:
        if accumulate:
            for station in self._arrive_time.keys():
                for i in range(len(self._arrive_time[station])):
                    if self._board_time[station][i] == 0:
                        self.waiting_time += self._t - self._arrive_time[station][i]
                    else:
                        self.waiting_time += (
                            self._board_time[station][i] - self._arrive_time[station][i]
                        )
        else:
            for station in self._arrive_time.keys():
                for i in range(len(self._arrive_time[station])):
                    if self._board_time[station][i] == 0:
                        self.waiting_time += min(
                            self._t - self._arrive_time[station][i],
                            self._t - self.wait_timestamp,
                        )
                    else:
                        self.waiting_time += min(
                            self._board_time[station][i]
                            - self._arrive_time[station][i],
                            self._board_time[station][i] - self.wait_timestamp,
                        )

            self.wait_timestamp = self._t

        return self.waiting_time

    def get_waiting_number(self, station=None):
        if station is None:
            return self.total_waiting_number
        else:
            waiting_number = 0
            for t in self._board_time[station]:
                if t == 0:
                    waiting_number += 1
            return waiting_number

    def get_total_waiting_time(self):
        return self.total_waiting_time

    def get_arrived_list(self):
        e

    def reset_waiting_time(self):
        for station in self._arrive_time.keys():
            index = range(len(self._arrive_time[station]))
            for i in reversed(index):
                if self._board_time[station][i] != 0:
                    self._arrive_time[station].pop(i)
                    self._board_time[station].pop(i)
        self.waiting_time = 0

    def set_wait_timestamp(self):
        self.wait_timestamp = self._t

    def board(self, station, onboard=0):
        # n = self.board_passenger[station]
        waiting_number = 0
        for t in self._board_time[station]:
            if t == 0:
                waiting_number += 1
        cap = self._max_onboard - onboard
        if cap == 0:
            return 0

        if cap >= waiting_number:
            # self.board_passenger[station] = 0
            for i in range(len(self._board_time[station])):
                if self._board_time[station][i] == 0:
                    self._board_time[station][i] = self._t
                    self.total_waiting_time += (
                        self._board_time[station][i] - self._arrive_time[station][i]
                    )
            # self._invalid_waiting_time[station] += self.waiting_time[station]
            self.total_waiting_number -= waiting_number
            return waiting_number
        else:
            board_num = 0
            for i in range(len(self._board_time[station])):
                if self._board_time[station][i] == 0:
                    board_num += 1
                    self._board_time[station][i] = self._t
                    self.total_waiting_time += (
                        self._board_time[station][i] - self._arrive_time[station][i]
                    )
                    if board_num == cap:
                        break
            # the_rest = n - cap
            # self._invalid_waiting_time[station] += self.waiting_time[station] * (cap / n)
            # self.board_passenger[station] = the_rest
            self.total_waiting_number -= cap
            return cap

    def alight(self, station):
        n = self.alight_passenger[station]
        self.alight_passenger[station] = 0
        return n

    def reset(self):
        self._t = self._startup_time
        self.total_waiting_number = 0
        self.wait_timestamp = self._startup_time

        for station, data in self._raw_data.items():
            # init
            self._raw_data_index[station] = 0
            self._fine_grained_data[station] = {}
            self._invalid_waiting_time[station] = 0
            self._arrive_time[station] = []
            self._board_time[station] = []
            self.board_passenger[station] = 0
            self.alight_passenger[station] = 0
            # self.waiting_time[station] = 0

            # accumulate passengerflow
            # util arrive the startup time
            time = data['time']
            board = data['board']
            alight = data['alight']
            for i in range(len(time)):
                t = utils.str2seconds(time[i])
                if self._t >= t:
                    self._raw_data_index[station] = i + 1
                    self.board_passenger[station] += board[i]
                    self.alight_passenger[station] += alight[i]
                    self.total_waiting_number += board[i]
                    # self.waiting_time[station] += (self._t - t) * board[i]
                    self.waiting_time += (self._t - t) * board[i]
                else:
                    if i != 0:
                        t1 = time[i - 1]
                        t1 = utils.str2seconds(t1)
                        alpha = (self._t - t1) / (t - t1)

                        board_num = int(board[i] * alpha)
                        alight_num = int(alight[i] * alpha)
                        self.board_passenger[station] += board_num
                        self.alight_passenger[station] += alight_num
                        self.total_waiting_number += board_num
                        # self.waiting_time[station] += (self._t - t1) * board_num
                        self.waiting_time += (self._t - t1) * board_num

                        rest_num = board[i] - board_num
                        if rest_num == 0:
                            self._fine_grained_data[station]['board'] = []
                        else:
                            self.update_fine_grained_data(
                                rest_num, self._t, t, station, 'board'
                            )
                            # step = (t - self._t) // rest_num
                            # time_stamp = [j for j in range(t, self._t, -step)]
                            # if len(time_stamp) > rest_num:
                            #     time_stamp = time_stamp[0:rest_num]
                            # self._fine_grained_data[station]['board'] = time_stamp

                        rest_num = alight[i] - alight_num
                        if rest_num == 0:
                            self._fine_grained_data[station]['alight'] = []
                        else:
                            self.update_fine_grained_data(
                                rest_num, self._t, t, station, 'alight'
                            )
                            # step = (t - self._t) // rest_num
                            # time_stamp = [j for j in range(t, self._t, -step)]
                            # if len(time_stamp) > rest_num:
                            #     time_stamp = time_stamp[0:rest_num]
                            # self._fine_grained_data[station]['alight'] = time_stamp
                    else:
                        t = utils.str2seconds(time[0])
                        avg_waiting_time = (
                            5 * 60
                        )  # Suppose the average waiting time of the first bus is 5 minutes
                        t1 = (
                            t - avg_waiting_time
                            if t - self._t > avg_waiting_time
                            else self._t
                        )

                        if board[0] == 0:
                            self._fine_grained_data[station]['board'] = []
                        else:
                            self.update_fine_grained_data(
                                board[0], t1, t, station, 'board'
                            )
                            # step = (t - t1) // board[0]
                            # time_stamp = [j for j in range(t, t1, -step)]
                            # if len(time_stamp) > board[0]:
                            #     time_stamp = time_stamp[0 : board[0]]
                            # self._fine_grained_data[station]['board'] = time_stamp

                        if alight[0] == 0:
                            self._fine_grained_data[station]['alight'] = []
                        else:
                            self.update_fine_grained_data(
                                alight[0], t1, t, station, 'alight'
                            )
                            # step = (t - t1) // alight[0]
                            # time_stamp = [j for j in range(t, t1, -step)]
                            # if len(time_stamp) > alight[0]:
                            #     time_stamp = time_stamp[0 : alight[0]]
                            # self._fine_grained_data[station]['alight'] = time_stamp
                    break

    def update_fine_grained_data(self, num, t1, t2, station, flag):
        step = (t2 - t1) // (num + 1)
        time_stamp = [i for i in range(t2, t1, -step)]
        if len(time_stamp) > num:
            time_stamp = time_stamp[1 : num + 1]
        self._fine_grained_data[station][flag] = time_stamp

    # def _get_waiting_time(self, station):
    #     arrive_time = self._arrive_time[station]
    #     board_time = self._board_time[station]
