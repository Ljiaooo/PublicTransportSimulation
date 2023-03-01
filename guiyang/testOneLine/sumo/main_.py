import traci
import sys
from window_controll.handleSignals import Widget
from window_controll.threads import SumoThread,DataRefreshThread
from window_controll.control_through_window import ControlFunctions
from PyQt5.QtWidgets import QApplication



if __name__ == '__main__':
    sumoBinary = "sumo-gui"
    sumoConfig = [sumoBinary, '-c', "./guiyang.sumocfg"]
    traci.start(sumoConfig)



    #route = 48 
    #step = 0
    #controllers = []
    #base_time = '06:29:50'
    #start_time_stamp = str2seconds(base_time)
    #sumo_controller = SumoController(route)
    #controllers.append(sumo_controller)
    #upPassengerflow = PassengerFlow(start_time_stamp, str(route), "up","0826", controllers[0])
    #upBusController = BusController(start_time_stamp, str(route), "up","0826", controllers[0])
    #downPassengerflow = PassengerFlow(start_time_stamp,str(route), "down","0826", controllers[0])
    #downBusController = BusController(start_time_stamp,str(route), "down","0826", controllers[0])
    #upBusController.set_passengerflow(upPassengerflow)
    #downBusController.set_passengerflow(downPassengerflow)

    #controllers[0].drawStopPoi()
    #controllers[0].selectRoute(0)
    #controllers[0].selectRoute(1)

    #data thread
    data_thread = DataRefreshThread()
    data_thread.start()

    #sumo thread
    control_funcs = ControlFunctions()
    sumo_thread= SumoThread(control_funcs)
    sumo_thread.start()


    fp = open("./sumo/Medize.qss", "r")
    app = QApplication([])
    app.setStyleSheet(fp.read())
    window = Widget()

    window.global_view_button.clicked.connect(window.global_focus)
    window.car_track_button.clicked.connect(window.track_signal)
    window.line_choose_button.clicked.connect(window.line_choose)
    window.statistics_combobox.currentIndexChanged.connect(window.changeStackedWidgetPage)
    data_thread.signal.connect(window.refresh_table)
    window.stackedWidget.setCurrentIndex(0)

    window.show()
    sys.exit(app.exec())


