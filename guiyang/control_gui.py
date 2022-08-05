import globalVal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from controller import Controller
import traci
import random
import time
import sys
from threading import Thread
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread,pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets
from mainwindow import Ui_SumoController
import matplotlib
matplotlib.use('Qt5Agg')


# a set of functions to control sumo with qt window
class ControlFunc():
    cur = 0
    track_status = 0
    stopNumDict = {47: 37, 48: 28, 263: 28}

    def changeFocus(self, controllers, to):
        cur = self.cur
        routeDict = {47: 0, 48: 1, 263: 2}
        if cur == to:
            return
        for controller in controllers:
            if (controller.route == cur and to != 0) or (cur == 0 and controller.route != to):
                controller.removeStopPoi()
                controller.removeHighlight()
                controller.toggleBusSelection()
            if cur != 0 and (controller.route == to and to != 0 or to == 0 and controller.route != cur):
                controller.focusRoute()
                controller.highlightRoute()
                controller.drawStopPoi(r=50)
                controller.toggleBusSelection()

        # 切换为全局视角(没有定义全局视角单独controller)
        if to == 0:
            traci.gui.setZoom("View #0", 1275.0)
            traci.gui.setOffset("View #0", 52074.7, 45704.6)
            traci.gui.setAngle("View #0", 62)
        else:
            controllers[routeDict[to]].focusRoute()
        self.cur = to

    def changeTrack(self, controllers):
        traci.gui.track(controllers[globalVal.trackIndex-1].lastBus)
        traci.gui.setZoom("View #0", 6500.0)

    def checkGlobalVal(self, controllers):
        # 每一步判断控制窗口传过来的全局变量
        if globalVal.onfocus != self.cur:
            self.changeFocus(controllers, globalVal.onfocus)
        if globalVal.change_track != self.track_status:
            self.changeTrack(controllers)
            self.track_status = globalVal.change_track

    # 按照设定产生乘客
    # probability=0.4 per min(最后一个站无乘客)
    def generatePassenger(self, step, controllers):
        if step % 60 == 0:
            for controller in controllers:
                for i in range(self.stopNumDict[controller.route]-1):
                    if random.random() < 0.4:
                        controller.addPassenger(
                            "{}_{}".format(controller.route, i))

    # 产生公交车
    # 1bus/5min
    def generateBus(self, step, controllers):
        if step % 300 == 0:
            for controller in controllers:
                controller.addBus()

    # 根据全局变量刷新sumo数据
    def refreshSumo(self, stopseq, controllers):
        # 1. 刷新每个站点poi颜色（随站点人数变化）
        if globalVal.onfocus == 0:
            for controller in controllers:
                controller.changePoiColorByPersonNum()
        else:
            controllers[stopseq[globalVal.onfocus]
                        ].changePoiColorByPersonNum()

        # 2. 刷新车辆颜色（随便人数变化）
        for controller in controllers:
            controller.changeBusColor()

    #每一步统计信息到全局变量保存
    def writeData(self,controllers):
        waitingTime = []
        waitingNum = []
        for controller in controllers:
            waitingNum.append(controller.getWaitingTimeAndPersonNum()[0])
            waitingTime.append(controller.getWaitingTimeAndPersonNum()[1])

        globalVal.data = waitingNum + waitingTime






#######################
#######################

class Widget(QMainWindow, Ui_SumoController):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        #self.figure = plt.figure()
        #self.canvas = FigureCanvas(self.figure)
        #self.plot_()

        # onfocus now  whole <- 0

        # 设置布局
        self.setWindowIcon(QIcon("./icon/icon.png"))
        hlayout = QtWidgets.QHBoxLayout(self.centralwidget)
        hlayout.addWidget(self.frame, 3)
        hlayout.addWidget(self.stackedWidget, 13)
        self.centralwidget.setLayout(hlayout)

        # pushbotton

        # 连接的绘制的方法

    #def plot_(self):
    #    ax = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])
    #    ax.plot([1, 2, 3, 4, 5])
    #    self.canvas.draw()


class SumoThread(Thread):
    def __init__(self, control_funcs, controllers):
        Thread.__init__(self)
        self.controllers = controllers
        self.control_funcs = control_funcs
        self.stopseq = {47: 0, 48: 1, 263: 2}

    def run(self):
        step = 0
        while step < 86400:

            self.control_funcs.checkGlobalVal(self.controllers)
            self.control_funcs.generateBus(step, self.controllers)
            self.control_funcs.generatePassenger(step, self.controllers)
            self.control_funcs.refreshSumo(self.stopseq, self.controllers)
            self.control_funcs.writeData(self.controllers)

            traci.simulation.step()

            step += 1


class DataRefreshThread(QThread):
    signal=pyqtSignal(list)

    def run(self):
        while True:
            self.signal.emit(globalVal.data)
            time.sleep(1)