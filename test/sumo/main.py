import traci
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QApplication
from sumo_controller import SumoController
from simulation.passengerflow import PassengerFlow
from simulation.bus_controller import BusController
from simulation.utils import str2seconds
from control_gui import *


if __name__ == '__main__':
    sumoBinary = "sumo-gui"
    sumoConfig = [sumoBinary, '-c', "./guiyang.sumocfg"]
    traci.start(sumoConfig)

    #route = 1
    route = 48 
    step = 0
    base_time = '06:29:50'
    controllers = []
    start_time_stamp = str2seconds(base_time)
    sumo_controller = SumoController(route)
    controllers.append(sumo_controller)
    #upPassengerflow = PassengerFlow(start_time_stamp, "_"+str(route), "up","0000", sumo_controller)
    #upBusController = BusController(start_time_stamp, "_"+str(route), "up","0000", sumo_controller)
    #downPassengerflow = PassengerFlow(start_time_stamp, "_"+str(route), "down","0000", sumo_controller)
    #downBusController = BusController(start_time_stamp, "_"+str(route), "down","0000", sumo_controller)
    upPassengerflow = PassengerFlow(start_time_stamp, str(route), "up","0826", controllers[0])
    upBusController = BusController(start_time_stamp, str(route), "up","0826", controllers[0])
    downPassengerflow = PassengerFlow(start_time_stamp,str(route), "down","0826", controllers[0])
    downBusController = BusController(start_time_stamp,str(route), "down","0826", controllers[0])
    upBusController.set_passengerflow(upPassengerflow)
    downBusController.set_passengerflow(downPassengerflow)



    controllers[0].drawStopPoi()
    controllers[0].selectRoute(0)
    controllers[0].selectRoute(1)

        #sumo thread
    control_funcs = ControlFunc()
    sumo_thread = SumoThread(control_funcs,controllers,upPassengerflow,upBusController, downPassengerflow,downBusController)
    sumo_thread.start()

    #table refresh thread
    statistics_thread=DataRefreshThread()
    statistics_thread.start()

    #slot functions 
    ########################
    def global_focus():
        globalVal.onfocus=0


    def focus_line(idx):
        lines=[0,47,48,263]
        if idx==0:
            return
        else:
            globalVal.onfocus=lines[idx]

    def track_signal():
        globalVal.change_track+=1
        globalVal.trackIndex=window.comboBox.currentIndex()

    def refresh_table():
        item=QTableWidgetItem(str(globalVal.data[0]))
        window.tableWidget.setItem(0,1,item)
        item=QTableWidgetItem(str(globalVal.data[1]))
        window.tableWidget.setItem(1,1,item)
        window.tableWidget.update()
    def changeStackedWidgetPage(index):
        window.stackedWidget.setCurrentIndex(index)



    ########################

    fp = open("./sumo/Medize.qss", "r")
    app = QApplication([])
    app.setStyleSheet(fp.read())
    window = Widget()


    #connect widget slot functions
    window.pushButton.clicked.connect(global_focus)
    window.comboBox.currentIndexChanged.connect(focus_line)
    window.pushButton_2.clicked.connect(track_signal)
    window.comboBox_2.currentIndexChanged.connect(changeStackedWidgetPage)
    statistics_thread.signal.connect(refresh_table)
    window.stackedWidget.setCurrentIndex(0)

    window.move(1240, -40)
    window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    print('done')
    window.show()
    sys.exit(app.exec())