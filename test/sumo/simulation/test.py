import json
import sys
import os
import pandas as pd
import transbigdata as tbd
from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
import numpy as np
import random

pardir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(pardir)
from simulation.simulator import Simulator
import simulation.utils as utils


def main():
    test_simulator()
    # test_bus()
    # test_passengerflow()

def test_simulator():
    simulator = Simulator('48', 'up', '0826')
    obs = simulator.reset()

    print('test simulator')

    while True:
        obs, reward, done, info = simulator.step(720)

def test_passengerflow():
    startup_time = utils.str2seconds('06:00:00')
    simulator = Simulator('48', 'up', '0826', startup_time=startup_time)

    def print_msg(simulator):
        waiting_number = simulator.passengerflow.get_waiting_number()
        waiting_time = simulator.passengerflow.get_waiting_time()
        msg = 'num: {}\ttime: {}'.format(waiting_number, waiting_time)
        print(msg)

    # print_msg(simulator)
    # obs = simulator.reset()
    # print_msg(simulator)
    # simulator.passengerflow.reset_waiting_time()

    # while True:
    #     for i in range(1):
    #         simulator.update()
    #     print_msg(simulator)
    simulator.passengerflow.reset()
    simulator.bus_controller.reset()
    end_time = utils.str2seconds('22:30:00')
    for i in range(end_time - startup_time):
        simulator.update()
    print_msg(simulator)

def test_bus():
    # line = '48'
    # date = '0826'
    # direction = 'up'
    # filename = 'data/{}/timetable/{}_{}_timetable.json'.format(line, date, direction)
    # with open(filename, 'r') as f:
    #     timetable = json.load(f)
    startup_time = utils.str2seconds('17:56:59')
    simulator = Simulator('48', 'up', '0826', startup_time=startup_time)
    # obs = simulator.reset()
    simulator.bus_controller.dispatch()
    print(utils.seconds2str(simulator._t))
    simulator.step(3 * 3600)

if __name__ == '__main__':
    main()
