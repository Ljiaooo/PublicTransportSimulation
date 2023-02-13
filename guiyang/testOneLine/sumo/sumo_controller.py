#TODO: 乘客下车站点如何设定

import re
import math

import traci
import pandas as pd
import random
import json
from xml.dom import minidom


class SumoController():

    # 添加公交线路
    #route <- int
    def __init__(self, route):
        #线路以固定三位数表示,例如001
        self.route = str(route).zfill(3)
        self.perosonNum = 0
        self.upBusNum = 0
        self.downBusNum = 0
        # 已经到达的公交idx
        #self.upArrivedBuses = []
        #self.downArrivedBuses = []
        #self.busOnTheUpRoad = []
        #self.busOnTheDownRoad = []
        self.arrivedBuses = []
        self.busOnTheRoad = []
        self.busList = {}
        self.colors = [(0, 128, 255), (28, 113, 226), (56, 99, 198), (85, 85, 170), (113, 71, 141),
                       (141, 56, 113), (170, 42, 85), (198, 28, 56), (226, 14, 28), (255, 0, 0)]

        self.busColors = [(89, 193, 115), (89, 175, 123), (89, 158, 132), (90, 141, 141), (90, 124, 149), (91, 106, 158), (91, 89, 167), (92, 72, 175), (92, 55, 184), (93, 38, 193)]

        # 初始化公交线路
        self.upEdges = list(pd.read_csv(
            "./route{}_up.csv".format(route))["route{}_up".format(route)])
        self.downEdges = list(pd.read_csv(
            "./route{}_down.csv".format(route))["route{}_down".format(route)])
        #0表示up，1表示down
        traci.route.add(self.route+'_0', self.upEdges)
        traci.route.add(self.route+'_1', self.downEdges)

        # 获取站点列表
        doc = minidom.parse("./stops.add.xml".format(self.route))
        self.stops = doc.getElementsByTagName("busStop")
        self.stopNum = int(len(self.stops)/2)

        for stop in self.stops:
            self.busList[stop.getAttribute("id")] = (stop.getAttribute(
                "lane"), stop.getAttribute("startPos"), stop.getAttribute("endPos"))
        

    # 添加公交车，注意默认载客量50,默认最大速度10m/s, 默认车站停车时间10s
    #公交车ID:aaabc+  前三位为线路，第四位为方向(0:up, 1:down),第五,六位表示车辆数量
    def addBus(self, direction, depart_time='now'):
        busNum = self.upBusNum if direction == 0 else self.downBusNum
        busId = "bus{}_{}_{}".format(self.route, direction,str(busNum).zfill(2))
        traci.vehicle.add(busId, "{}_{}".format(self.route,direction), line=self.route, typeID="bus", depart=depart_time, departPos="0.0")
        for stop in self.stops: 
            stopID = stop.getAttribute('id')
            if stopID[4] == str(direction):
                traci.vehicle.setBusStop(busId, stopID, duration=10)
        if direction== 0:
            self.upBusNum += 1
        elif direction== 1:
            self.downBusNum +=1


    # 将到达的车辆id加入列表
    def updataBusLists(self):
        arrivedBuses = list(traci.simulation.getArrivedIDList())
        departedBuses = list(traci.simulation.getDepartedIDList())
        if arrivedBuses:
            self.arrivedBuses+=arrivedBuses
            self.busOnTheRoad = [bus for bus in self.busOnTheRoad if bus not in self.arrivedBuses]
            #self.upArrivedBuses+=[bus for bus in arrivedBuses if bus[4]=='0']
            #self.downArrivedBuses+=[bus for bus in arrivedBuses if bus[4]=='1']
            #self.busOnTheUpRoad = [bus for bus in self.busOnTheUpRoad if bus not in self.upArrivedBuses]
            #self.busOnTheDownRoad = [bus for bus in self.busOnTheDownRoad if bus not in self.downArrivedBuses]
        if departedBuses:
            self.busOnTheRoad+=departedBuses
            #self.busOnTheUpRoad += departedBuses
            #self.busOnTheDownRoad += departedBuses


    # 车辆根据人数改变颜色
    def changeBusColor(self):
        for i in range(self.upBusNum):
            busID = "bus{}_0_{}".format(self.route, str(i).zfill(2))
            # 排除已经到达车辆
            #if busID in self.upArrivedBuses:
            if busID in self.arrivedBuses:
                continue
            onboard = traci.vehicle.getPersonNumber(busID)
            index = math.floor(onboard/8)
            if index > 9:
                index = 9
            traci.vehicle.setColor(busID, self.busColors[index])
        for i in range(self.downBusNum):
            busID = "bus{}_1_{}".format(self.route, str(i).zfill(2))
            # 排除已经到达车辆
            #if busID in self.downArrivedBuses:
            if busID in self.arrivedBuses:
                continue
            onboard = traci.vehicle.getPersonNumber(busID)
            index = math.floor(onboard/8)
            if index > 9:
                index = 9
            traci.vehicle.setColor(busID, self.busColors[index])


    # 添加乘客
    def addPassenger(self, busStop):
        # personPos = random.uniform(
        #    float(self.busList[busStop][1]), float(self.busList[busStop][2]))

        personID = "person{}_{}".format(busStop, self.perosonNum)
        personPos = float(self.busList[busStop][1])+0.1
        #personPos = 0
        traci.person.add(personID, self.busList[busStop][0][:-2], personPos)

        # 添加乘客乘坐线路以及下车地点(最后一个站点无乘客，下车地点暂设随机)
        dropEdge = self.busList["{}_{}_{}".format(self.route,busStop[4],self.stopNum-1)][0][:-2]
        traci.person.appendWalkingStage(personID, self.busList[busStop][0][:-2], personPos, stopID=busStop)
        traci.person.appendDrivingStage(personID, toEdge=dropEdge, lines=self.route, stopID ="{}_{}_{}".format(self.route,busStop[4],self.stopNum-1))
        self.perosonNum += 1



    def drawStopPoi(self, r=40):
        pointsNum = 10  # polygon点数
        r = r  # polygon圆形半径
        angle = (2*math.pi)/pointsNum
        for stop in self.stops:
            edge = stop.getAttribute("lane")[:-2]
            pos = float(stop.getAttribute("startPos"))
            shape = []
            X, Y = traci.simulation.convert2D(edge, pos)
            for i in range(pointsNum+1):
                x = X+r*math.sin(i*angle)
                y = Y+r*math.cos(i*angle)
                shape.append((x, y))

            # color define the stop point color
            traci.polygon.add(stop.getAttribute("id"), lineWidth=100,
                              shape=shape, color=(250, 8, 8), layer=102, fill=True)


    # 根据站点人数设置站点颜色变化,超过30人均显示红色
    def changePoiColorByPersonNum(self):
        for i in range(self.stopNum):
            allWaitingPerson = traci.busstop.getPersonIDs(
                "{}_0_{}".format(self.route, str(i).zfill(2)))
            currentLineWaitingPerson = len(
                [person for person in allWaitingPerson if person[:11] == "person{}_0".format(self.route)])
            index = math.floor(currentLineWaitingPerson/2)
            if index > 9:
                index = 9
            traci.polygon.setColor("{}_0_{}".format(
                self.route,str(i).zfill(2)), self.colors[index])

        for i in range(self.stopNum):
            allWaitingPerson = traci.busstop.getPersonIDs(
                "{}_1_{}".format(self.route, str(i).zfill(2)))
            currentLineWaitingPerson = len(
                [person for person in allWaitingPerson if person[:11] == "person{}_1".format(self.route)])
            index = math.floor(currentLineWaitingPerson/2)
            if index > 9:
                index = 9
            traci.polygon.setColor("{}_1_{}".format(
                self.route,str(i).zfill(2)), self.colors[index])


    #选择线路， 显示或者隐藏线路
    def selectRoute(self,direction):
        if direction == 0:
            for edge in self.upEdges:
                traci.gui.toggleSelection(edge, objType='edge')
        else:
            for edge in self.downEdges:
                traci.gui.toggleSelection(edge, objType='edge')


    # 选择车辆，显示或者隐藏该线路上的车辆
    def selectBuses(self, direction):
        busNum = self.upBusNum if direction == 0 else self.downBusNum
        for i in range(busNum):
            busID = "bus{}_{}_{}".format(self.route, direction, str(i).zfill(2))
            if busID not in traci.simulation.getArrivedIDList():
                traci.gui.toggleSelection(busID, objType = 'vehicle')


    # 选择乘客， 显示或隐藏
    def selectPassengers(self):
        pass


    # 选择polygon， 显示或者隐藏
    def seletcPolygon(self):
        pass





