import traci
from PyQt5 import QtCore
from control_gui import *

import globalVal





if __name__ == "__main__":

    sumoBinary = "sumo-gui"
    sumoConfig = [sumoBinary, '-c', "xml_files/guiyang.sumocfg"]
    traci.start(sumoConfig)

    controllers = []
    controller47 = Controller(route=47)
    controller48 = Controller(route=48)
    controller263 = Controller(route=263)
    controllers.append(controller47)
    controllers.append(controller48)
    controllers.append(controller263)

    # start UI, add stop poi(route polygon loaded with net in config)
    controller47.drawStopPoi(r=50)
    controller48.drawStopPoi(r=50)
    controller263.drawStopPoi(r=50)

    
    #sumo thread
    control_funcs = ControlFunc()
    sumo_thread = SumoThread(control_funcs,controllers)
    sumo_thread.start()



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

    def track_signal(window):
        globalVal.change_track+=1
        globalVal.trackIndex=window.comboBox.currentIndex()


    ########################

    fp = open("Medize.qss", "r")
    app = QApplication([])
    app.setStyleSheet(fp.read())
    window = Widget()


    #connect widget slot functions
    window.pushButton.clicked.connect(global_focus)
    window.comboBox.currentIndexChanged.connect(focus_line)
    window.pushButton_2.clicked.connect(lambda:track_signal(window))

    window.move(1300, 0)
    window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    window.show()
    sys.exit(app.exec())
