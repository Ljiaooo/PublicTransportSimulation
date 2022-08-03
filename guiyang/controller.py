import re
import math

import traci
import pandas as pd
import random
from xml.dom import minidom


class Controller():

    # 添加公交线路
    #route <- int
    def __init__(self, route):
        self.route = route
        self.viewport = pd.read_csv("csv_files/viewport.csv")[str(self.route)]
        self.stopNumDict = {47: 37, 48: 28, 263: 28}
        self.lastBus = None
        self.perosonNum = 0
        self.busNum = 0
        self.busList = {}
        self.colors = [(0, 128, 255), (28, 113, 226), (56, 99, 198), (85, 85, 170), (113, 71, 141),
                       (141, 56, 113), (170, 42, 85), (198, 28, 56), (226, 14, 28), (255, 0, 0)]

        self.busColors = [(102, 255, 102), (102, 255, 178), (102, 255, 255), (102, 178, 255), (
            102, 102, 255), (78, 102, 255), (255, 102, 255), (255, 102, 178), (255, 51, 153), (255, 0, 127)]

        # 初始化公交线路
        edges = list(pd.read_csv(
            "csv_files/route{}.csv".format(self.route))["route{}".format(self.route)])
        traci.route.add(str(self.route), edges)

        # 获取站点列表
        doc = minidom.parse("xml_files/stop_{}.add.xml".format(self.route))
        self.stops = doc.getElementsByTagName("busStop")
        self.stopNum = len(self.stops)

        for stop in self.stops:
            self.busList[stop.getAttribute("id")] = (stop.getAttribute(
                "lane"), stop.getAttribute("startPos"), stop.getAttribute("endPos"))

    # 添加公交车，注意默认载客量50,默认最大速度10m/s

    def addBus(self):
        busId = "bus{}_{}".format(self.route, self.busNum)
        traci.vehicle.add(busId, str(self.route), line=str(
            self.route), typeID="bus", depart="now", departPos="0.0")
        for stop in self.stops:
            traci.vehicle.setBusStop(
                busId, stop.getAttribute("id"), duration=40)
        self.lastBus = busId
        self.busNum += 1

    # 车辆根据人数改变颜色
    def changeBusColor(self):
        for i in range(self.busNum):
            busID = "bus{}_{}".format(self.route, i)
            onboard = traci.vehicle.getPersonNumber(busID)
            index = math.floor(onboard/5)
            if index > 9:
                index = 9
            traci.vehicle.setColor(busID, self.busColors[index])

    # 添加乘客
    def addPassenger(self, busStop):
        # personPos = random.uniform(
        #    float(self.busList[busStop][1]), float(self.busList[busStop][2]))

        personPos = float(self.busList[busStop][1])+0.1
        traci.person.add(busStop+"_{}".format(self.perosonNum),
                         self.busList[busStop][0][:-2], personPos)

        # 添加乘客乘坐线路以及下车地点(最后一个站点无乘客，下车地点暂设随机)
        if busStop[-2] == '_':
            stop = int(busStop[-1])+1
        else:
            stop = int(busStop[-2:])+1
        stopID = "{}_{}".format(self.route, int(
            random.random()*(self.stopNum-stop))+stop)
        traci.person.appendWalkingStage(
            busStop+"_{}".format(self.perosonNum), self.busList[busStop][0][:-2], personPos, stopID=busStop)
        traci.person.appendDrivingStage(busStop+"_{}".format(self.perosonNum),
                                        toEdge=self.busList[busStop][0][:-2], lines=str(self.route), stopID=stopID)
        self.perosonNum += 1

    # 聚焦某一条线路
    def focusRoute(self):
        traci.gui.setZoom("View #0", self.viewport[0])
        traci.gui.setOffset("View #0", self.viewport[1], self.viewport[2])
        traci.gui.setAngle("View #0", self.viewport[3])
        traci.gui.track("")

    # 追踪最近发出的车辆

    def trackBus(self):
        traci.gui.track(self.lastBus)

    def highlightRoute(self):
        doc = minidom.parse(
            "xml_files/highlight{}.poly.xml".format(self.route))
        route = doc.getElementsByTagName("poly")[0]
        colorstring = route.getAttribute("color")
        shapestring = route.getAttribute("shape")
        color = tuple(map(int, re.findall(r'\d+', colorstring)))
        shape = [tuple(map(float, item.split(",")))
                 for item in shapestring.split(" ")]
        layer = route.getAttribute("layer")
        traci.polygon.add("route{}".format(self.route),
                          shape=shape, color=color, layer=layer, lineWidth=20.0)

    def removeHighlight(self):
        traci.polygon.remove("route{}".format(self.route))

    def drawStopPoi(self, r=40):
        pointsNum = 10  # polygon点数
        r = r  # polygon圆形半径
        angle = (2*math.pi)/pointsNum
        for stop in self.stops:
            edge = stop.getAttribute("lane")[:-2]
            pos = float(stop.getAttribute("startPos"))+10.0
            shape = []
            X, Y = traci.simulation.convert2D(edge, pos)
            for i in range(pointsNum+1):
                x = X+r*math.sin(i*angle)
                y = Y+r*math.cos(i*angle)
                shape.append((x, y))

            traci.polygon.add("poi"+stop.getAttribute("id"), lineWidth=100,
                              shape=shape, color=(250, 8, 8), layer=102, fill=True)

    # 根据站点人数设置站点颜色变化,超过30人均显示红色

    def changePoiColorByPersonNum(self):
        for i in range(self.stopNumDict[self.route]):
            # index=math.floor(traci.busstop.getPersonCount("{}_{}".format(self.route,i))/5)
            # busesOnTheEdge = traci.edge.getLastStepVehicleIDs(
            #    self.stops[i].getAttribute("lane")[:-2])
            #personOnTheBus = []
            # for bus in busesOnTheEdge:
            #    personOnTheBus += list(traci.vehicle.getPersonIDList(bus))

            # perosonOnTheEdge = traci.edge.getLastStepPersonIDs(
            #    self.stops[i].getAttribute("lane")[:-2])
            # allWaitingPerson = [
            #    i for i in perosonOnTheEdge if i not in personOnTheBus]
            # currentLineWaitingPerson = [
            #    i for i in allWaitingPerson if i[:2] == str(self.route)]
            allWaitingPerson = traci.busstop.getPersonIDs(
                "{}_{}".format(self.route, i))
            nameWidth = 3 if self.route == 263 else 2
            currentLineWaitingPerson = len(
                [i for i in allWaitingPerson if i[:nameWidth] == str(self.route)])
            index = math.floor(currentLineWaitingPerson/2)
            if index > 9:
                index = 9
            traci.polygon.setColor("poi{}_{}".format(
                self.route, i), self.colors[index])

    def removeStopPoi(self):
        for i in range(self.stopNumDict[self.route]):
            traci.polygon.remove("poi{}_{}".format(self.route, i))
