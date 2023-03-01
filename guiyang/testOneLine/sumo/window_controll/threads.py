import time
import traci
import globalVal
from threading import Thread
from threading import Thread
from PyQt5.QtCore import QThread,pyqtSignal
from simulation.passengerflow import PassengerFlow
from simulation.bus_controller import BusController
from sumo_controller import SumoController
from simulation.utils import str2seconds



class SumoThread(Thread):
    def __init__(self, control_funcs):
        Thread.__init__(self)
        self.control_funcs = control_funcs
        route = 48 
        self.controllers = []
        base_time = '06:29:50'
        start_time_stamp = str2seconds(base_time)
        sumo_controller = SumoController(route)
        self.controllers.append(sumo_controller)
        self.upPassengerflow = PassengerFlow(start_time_stamp, str(route), "up","0826", self.controllers[0])
        self.upBusController = BusController(start_time_stamp, str(route), "up","0826", self.controllers[0])
        self.downPassengerflow = PassengerFlow(start_time_stamp,str(route), "down","0826", self.controllers[0])
        self.downBusController = BusController(start_time_stamp,str(route), "down","0826", self.controllers[0])
        self.upBusController.set_passengerflow(self.upPassengerflow)
        self.downBusController.set_passengerflow(self.downPassengerflow)

        self.controllers[0].drawStopPoi()
        self.controllers[0].selectRoute(0)
        self.controllers[0].selectRoute(1)


    def run(self):
        step = 0
        while step < 86400:

            self.controllers[0].updateBusLists()
            self.upPassengerflow.sumo_update()
            self.downPassengerflow.sumo_update()
            self.upBusController.sumo_update()
            self.downBusController.sumo_update()
            self.control_funcs.checkGlobalVals(self.controllers)
            self.control_funcs.refreshSumoColor(self.controllers)
            self.control_funcs.writeData(self.controllers)

            self.controllers[0].changeBusColor()
            self.controllers[0].changePoiColorByPersonNum()
            traci.simulation.step()

            step += 1


class DataRefreshThread(QThread):
    signal=pyqtSignal(dict)

    def run(self):
        while True:
            self.signal.emit(globalVal.data)
            time.sleep(1)