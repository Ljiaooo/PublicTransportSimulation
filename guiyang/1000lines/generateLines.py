#TODO: 解决站名重复问题
#TODO: 双向控制问题

import traci
import random
import math
import transbigdata as tbd
import sumolib
import requests
import json
import pandas as pd
from xml.dom import minidom



sumoBinary = "sumo-gui"
sumoConfig = [sumoBinary, '-c', "./Test/guiyang.sumocfg"]
traci.start(sumoConfig)
traci.simulation.step()
net = sumolib.net.readNet('./xml_files/guiyang.net.xml')




def getRandomCoord(center=(53865.6, 41958.0), radius=3000):
    randomR = random.random()*radius
    randomAngle = 2*math.pi*random.random()
    x = randomR*math.cos(randomAngle)
    y = randomR*math.sin(randomAngle)
    return center[0] + x, center[1] + y


def getRandomStopNum(minNum = 25, maxNum =  35):
    return minNum+int((maxNum-minNum)*random.random())


def request_url_get(url):
    try:
        r = requests.get(url=url, timeout=30)
        if r.status_code == 200:
            return r.text
        return None
    except: 
        print('Got error!')
        return None


def getStopName(lon, lat, curStopNames):
    key = 'a501f49646a8dbf082d7cc79b6fe845c'
    lon = round(lon, 6)
    lat = round(lat, 6)
    url = 'https://restapi.amap.com/v3/geocode/regeo?output=json&location={},{}&key={}&radius=1000&extensions=all&batch=false&roadlevel=0'.format(lon,lat,key)
    result = request_url_get(url)
    result = json.loads(result)
    pois = result['regeocode']['pois']
    roads = result['regeocode']['roads']
    aois = result['regeocode']['aois']
    #if len(pois)>20:
    #    pois = [pois[i]['name'] for i in range(20)]
    #else:
    #    pois = [pois[i]['name'] for i in range(len(pois))]

    #if len(roads)>5:
    #    roads = [roads[i]['name'] for i in range(5)]
    #else:
    #    roads = [roads[i]['name'] for i in range(len(roads))]
    pois = [pois[i]['name'] for i in range(len(pois))]
    roads = [roads[i]['name'] for i in range(len(roads))]
    aois = [aois[i]['name'] for i in range(len(aois))]
    name_candinates = pois+roads
    if not name_candinates:
        return -1
    fina_name =name_candinates[int(len(name_candinates)*random.random())]
    timeout=0
    while(fina_name in curStopNames):
        timeout += 1
        if timeout>50:
            return -1
        fina_name = name_candinates[int(len(name_candinates)*random.random())]
    print(fina_name)
    return fina_name


def getRandomEndCoord(startPoint, radius):
    return startPoint[0]+math.cos(2*math.pi*random.random())*radius, startPoint[1]+math.sin(2*math.pi*random.random())*radius


def coordinatesTransform(laneID, pos):
    x, y = sumolib.geomhelper.positionAtShapeOffset(net.getLane(laneID).getShape(), pos)
    lon, lat = net.convertXY2LonLat(x, y)
    return lon, lat


def getStopNameAtLane(laneID, pos, curStopNames):
    lon, lat = coordinatesTransform(laneID, pos)
    return getStopName(lon, lat, curStopNames)


#write all lines' stops in one file, better to save each line temporarily
def generateStopsXml(stopNames, stopOnTheUpLane,stopOnTheDownLane, upStopStartPos,downStopStartPos, line):
    save_path = './testOneLine'
    dom = minidom.Document()
    addition_node = dom.createElement('addition')
    dom.appendChild(addition_node)
    line = str(line).zfill(3)
    #up
    for i in range(len(stopNames)):
        busStop_node = dom.createElement('busStop')
        busStop_node.setAttribute('id','{}_0_{}'.format(line,str(i).zfill(2)))
        busStop_node.setAttribute('name',stopNames[i])
        busStop_node.setAttribute('lane',str(stopOnTheUpLane[i]))
        busStop_node.setAttribute('startPos',str(upStopStartPos[i]))
        busStop_node.setAttribute('endPos',str(upStopStartPos[i]+10))
        busStop_node.setAttribute('friendlyPos','True')
        busStop_node.setAttribute('lines', line)
        busStop_node.setAttribute('personCapacity','50')
        addition_node.appendChild(busStop_node)
    #down
    for i in range(len(stopNames)):
        busStop_node = dom.createElement('busStop')
        busStop_node.setAttribute('id','{}_1_{}'.format(line,str(i).zfill(2)))
        busStop_node.setAttribute('name',stopNames[len(stopNames)-1-i])
        busStop_node.setAttribute('lane',str(stopOnTheDownLane[i]))
        busStop_node.setAttribute('startPos',str(downStopStartPos[i]))
        busStop_node.setAttribute('endPos',str(downStopStartPos[i]+10))
        busStop_node.setAttribute('friendlyPos','True')
        busStop_node.setAttribute('lines', line)
        busStop_node.setAttribute('personCapacity','50')
        addition_node.appendChild(busStop_node)

    with open('{}/stops.add.xml'.format(save_path),'w',encoding='utf-8') as f:
        dom.writexml(f,indent='',addindent='\t', newl='\n', encoding='UTF-8')


def generateRouteCSV(edges,line, direction):
    save_path = './testOneLine'
    data = pd.DataFrame({'route{}_{}'.format(line, direction):edges})
    data.to_csv('{}/route{}_{}.csv'.format(save_path, line,direction),encoding='utf-8',index=False)


def generateStopsWithIDJson(stopNames, line):
    save_path = './testOneLine'
    id2name = {}
    name2id = {}
    id2name['up'] = {}
    id2name['down'] = {}
    name2id['up'] = {}
    name2id['down'] = {}
    for i in range(2*len(stopNames)):
        if i < len(stopNames):
            id2name['up'][str(i+1)]=stopNames[i]
            name2id['up'][stopNames[i]] = i+1
        else:
            id2name['down'][str(i+1)]=stopNames[2*len(stopNames)-i-1]
            name2id['down'][stopNames[2*len(stopNames)-i-1]] = i+1
    id2name_filename = '{}/_{}_id2name.json'.format(save_path, line)
    name2id_filename = '{}/_{}_name2id.json'.format(save_path, line)
    with open(id2name_filename,'w',encoding='utf-8') as f:
        json.dump(id2name,f,indent=2,ensure_ascii=False)
    with open(name2id_filename,'w',encoding='utf-8') as f:
        json.dump(name2id,f,indent=2, ensure_ascii=False)


def generateStopNameWithDistanceJson(stopNames, upDistanceList,downDistanceList, line):
    save_path = './testOneLine'
    up = {}
    down={}
    for i in range(len(stopNames)-1):
        up[stopNames[i]] = upDistanceList[i]
        down[stopNames[len(stopNames)-i-1]] = downDistanceList[i]

    up_save_path = '{}/_{}_up_distance.json'.format(save_path, line)
    down_save_path = '{}/_{}_down_distance.json'.format(save_path, line)
    with open(up_save_path,'w',encoding='utf-8') as f:
        json.dump(up, f, indent=2,ensure_ascii=False)
    with open(down_save_path,'w',encoding='utf-8') as f:
        json.dump(down, f, indent=2, ensure_ascii=False)


#25~35站点数量
LINES_DEMAND = 1
MIN_DISTANCE_BETWEEN_STOPS = 350
MIN_STOP_NUM = 25
MAX_STOP_NUM = 35
MIN_STOP_ON_THE_LANE_LENGTH = 30

#x,y
STRAIGHT_LINE_DISTANCE = 16000
#the length of a stop
STOP_LENGTH = 10

curLinesNum = 1

#data to write: stop names, stop ID, route
while curLinesNum <= LINES_DEMAND:
    stopNames = []
    upEdges = []
    downEdges= []
    upDistanceBetweenStopsList = []

    stopOnTheUpLane = []
    stopOnTheDownLane = []
    upStopStartPos = []
    downStopStartPos = []

    upRouteLength = 0
    downRouteLength = 0
    randomStartPoint = getRandomCoord()
    randomEndPoint = getRandomEndCoord(randomStartPoint,STRAIGHT_LINE_DISTANCE)
    startNeighborLanes = net.getNeighboringLanes(randomStartPoint[0],randomStartPoint[1], 100)
    endNeighborLanes = net.getNeighboringLanes(randomEndPoint[0],randomEndPoint[1], 100)
    while not startNeighborLanes or not endNeighborLanes:
        randomStartPoint = getRandomCoord()
        randomEndPoint = getRandomEndCoord(randomStartPoint,STRAIGHT_LINE_DISTANCE)
        startNeighborLanes = net.getNeighboringLanes(randomStartPoint[0],randomStartPoint[1], 100)
        endNeighborLanes = net.getNeighboringLanes(randomEndPoint[0],randomEndPoint[1], 100)
    
    #startLaneID 
    startLaneID = startNeighborLanes[0][0].getID()
    endLaneID = endNeighborLanes[0][0].getID()
    startEdgeID = startLaneID[:-2]
    endEdgeID = endLaneID[:-2]

    #find path from start edge to end edge
    #make sure the edge at least has 0 and 1 lane
    edges = list(traci.simulation.findRoute(fromEdge = startEdgeID, toEdge = endEdgeID).edges)
    if not edges:
        continue
    stopNum = getRandomStopNum()
    distanceBetweenStops = 0
    stopOnTheUpLane.append(edges[0]+'_1')
    upStopStartPos.append(0.0)
    stopName=getStopNameAtLane(edges[0]+'_1',0.0,stopNames)
    if stopName == -1:
        continue
    stopNames.append(stopName)
    curStopIndex=1
    satisfied = True
    for edge in edges:
        if curStopIndex>=stopNum:
            finalEndEdge = edge
            break
        upEdges.append(edge)
        curLaneLength = traci.lane.getLength(edge+'_1')
        distanceBetweenStops+= int(curLaneLength)
        upRouteLength+= int(curLaneLength)
        if distanceBetweenStops>MIN_DISTANCE_BETWEEN_STOPS and  curLaneLength>MIN_STOP_ON_THE_LANE_LENGTH:
            upPos = curLaneLength-STOP_LENGTH
            stopOnTheUpLane.append(edge+'_1')
            upStopStartPos.append(upPos)
            if curStopIndex>0:
                upDistanceBetweenStopsList.append(distanceBetweenStops)
            distanceBetweenStops = 0
            stopName = getStopNameAtLane(edge+'_1',upPos,stopNames)
            if stopName == -1:
                satisfied = False
                break
            stopNames.append(stopName)
            curStopIndex+=1

    if curStopIndex<stopNum or not satisfied:
        print('Not enough stops')
        continue

    #get down direction data
    downEdges = list(traci.simulation.findRoute(finalEndEdge, startEdgeID).edges)
    for edge in downEdges:
        downRouteLength+=traci.lane.getLength(edge+'_1')
    downDistanceBetweenStopsList = list(reversed([upDistanceBetweenStopsList[i]+int((downRouteLength-upRouteLength)/(stopNum-1)-20) for i in range(stopNum-1)]))
    print('------------')
    print(downDistanceBetweenStopsList)
    print('------------')
    curDistanceBetweenStops = 0
    stopOnTheDownLane.append(downEdges[0]+'_1')
    downStopStartPos.append(0.)
    curStopIndex = 0
    for i in range(1,len(downEdges)):
        curLaneLength = traci.lane.getLength(downEdges[i]+'_1')
        curDistanceBetweenStops+= int(curLaneLength)
        if curDistanceBetweenStops>downDistanceBetweenStopsList[curStopIndex]:
            stopOnTheDownLane.append(downEdges[i]+'_1')
            curDistanceBetweenStops = curDistanceBetweenStops-downDistanceBetweenStopsList[curStopIndex]
            temp=curLaneLength- curDistanceBetweenStops
            if temp>0:
                downStopStartPos.append(temp)
            else:
                downStopStartPos.append(0)
            curStopIndex+=1
            if curStopIndex>=len(downDistanceBetweenStopsList):
                break
        
    if curStopIndex<len(downDistanceBetweenStopsList):
        print(curStopIndex,stopNum)
        continue

        

    #write data to file
    generateRouteCSV(upEdges,curLinesNum,'up')
    generateRouteCSV(downEdges,curLinesNum,'down')
    generateStopNameWithDistanceJson(stopNames,upDistanceBetweenStopsList,downDistanceBetweenStopsList,curLinesNum)
    generateStopsWithIDJson(stopNames, curLinesNum)
    generateStopsXml(stopNames,stopOnTheUpLane,stopOnTheDownLane, upStopStartPos,downStopStartPos, curLinesNum)


    #finished one line
    curLinesNum+=1


    for edge in upEdges:
        traci.gui.toggleSelection(edge,objType='edge')
    print('done!')
traci.simulation.step()