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




def getRandomCoord(center=(53865.6, 41958.0), radius=8000):
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



def coordinatesTransform(laneID, pos):
    x, y = sumolib.geomhelper.positionAtShapeOffset(net.getLane(laneID).getShape(), pos)
    lon, lat = net.convertXY2LonLat(x, y)
    return lon, lat


def getStopNameAtLane(laneID, pos, curStopNames):
    lon, lat = coordinatesTransform(laneID, pos)
    return getStopName(lon, lat, curStopNames)


#write all lines' stops in one file, better to save each line temporarily
def generateStopsXml(stopNames, stopOnTheLane, stopStartPos, line):
    save_path = './testOneLine'
    dom = minidom.Document()
    addition_node = dom.createElement('addition')
    dom.appendChild(addition_node)
    for i in range(len(stopNames)):
        busStop_node = dom.createElement('busStop')
        busStop_node.setAttribute('id','{}_{}'.format(line,i))
        busStop_node.setAttribute('name',stopNames[i])
        busStop_node.setAttribute('lane',str(stopOnTheLane[i]))
        busStop_node.setAttribute('startPos',str(stopStartPos[i]))
        busStop_node.setAttribute('endPos',str(stopStartPos[i]+10))
        busStop_node.setAttribute('friendlyPos','True')
        busStop_node.setAttribute('lines', str(line))
        busStop_node.setAttribute('personCapacity','50')
        addition_node.appendChild(busStop_node)

    with open('{}/stops.add.xml'.format(save_path),'w',encoding='utf-8') as f:
        dom.writexml(f,indent='',addindent='\t', newl='\n', encoding='UTF-8')


def generateRouteCSV(lanes,line):
    save_path = './testOneLine'
    edges = [lane[:-2] for lane in lanes]
    data = pd.DataFrame({'route{}'.format(line):edges})
    data.to_csv('{}/route{}.csv'.format(save_path, line),encoding='utf-8',index=False)


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
            name2id['up'][stopNames[i]] = str(i+1)
        else:
            id2name['down'][str(i+1)]=stopNames[2*len(stopNames)-i-1]
            name2id['down'][stopNames[2*len(stopNames)-i-1]] = str(i+1)
    id2name_filename = '{}/{}_id2name.json'.format(save_path, line)
    name2id_filename = '{}/{}_name2id.json'.format(save_path, line)
    with open(id2name_filename,'w',encoding='utf-8') as f:
        json.dump(id2name,f,indent=2,ensure_ascii=False)
    with open(name2id_filename,'w',encoding='utf-8') as f:
        json.dump(name2id,f,indent=2, ensure_ascii=False)


def generateStopNameWithDistanceJson(stopNames, distanceList, line):
    save_path = './testOneLine'
    up = {}
    down={}
    for i in range(len(distanceList)):
        up[stopNames[i]] = distanceList[i]
        down[stopNames[len(distanceList)-i]] = distanceList[len(distanceList)-i-1]

    up_save_path = '{}/{}_up_distance.json'.format(save_path, line)
    down_save_path = '{}/{}_down_distance.json'.format(save_path, line)
    with open(up_save_path,'w',encoding='utf-8') as f:
        json.dump(up, f, indent=2,ensure_ascii=False)
    with open(down_save_path,'w',encoding='utf-8') as f:
        json.dump(down, f, indent=2, ensure_ascii=False)


#25~35站点数量
LINES_DEMAND = 1
MIN_DISTANCE_BETWEEN_STOPS = 600
MIN_STOP_NUM = 25
MAX_STOP_NUM = 35
#the length of a stop
STOPLENGTH = 10

curLinesNum = 1

#data to write: stop names, stop ID, route
while curLinesNum <= LINES_DEMAND:
    stopNames = []
    lanes = []
    distanceBetweenStopsList = []

    stopOnTheLane = []
    stopStartPos = []

    randomStartPoint = getRandomCoord()
    neighborLanes = net.getNeighboringLanes(randomStartPoint[0],randomStartPoint[1], 100)
    while not neighborLanes:
        randomStartPoint = getRandomCoord()
        neighborLanes = net.getNeighboringLanes(randomStartPoint[0],randomStartPoint[1], 100)
    
    #startLaneID 
    startLaneID = neighborLanes[0][0].getID()
    lanes.append(startLaneID)
    stopName = getStopNameAtLane(startLaneID,0,stopNames)
    if stopName==-1:
        continue
    stopNames.append(stopName)
    stopOnTheLane.append(startLaneID)
    stopStartPos.append(0.)

    #get random stops number
    stopNum = getRandomStopNum()

    curStopIndex = 0
    curLane = startLaneID
    satisfied = True
    distanceBetweenStops = 0
    while curStopIndex<stopNum:
        nextLaneInfo = traci.lane.getLinks(curLane, False)
        if not nextLaneInfo:
            satisfied = False
            break
        nextLaneID = nextLaneInfo[0][0]
        nextLaneLength = traci.lane.getLength(nextLaneID)
        curLane = nextLaneID
        curLaneLength = int(nextLaneLength)
        lanes.append(curLane)
        distanceBetweenStops+=curLaneLength
        if distanceBetweenStops>MIN_DISTANCE_BETWEEN_STOPS and curLaneLength>STOPLENGTH:
            distanceBetweenStopsList.append(distanceBetweenStops)
            stopName = getStopNameAtLane(curLane,curLaneLength-STOPLENGTH,stopNames)
            if stopName==-1:
                satisfied=False
                break
            stopNames.append(stopName)
            stopOnTheLane.append(curLane)
            stopStartPos.append(curLaneLength-STOPLENGTH)
            distanceBetweenStops = 0
            curStopIndex+=1

    #stop numbers < 25
    if not satisfied:
        continue

    #write data to file
    generateRouteCSV(lanes,curLinesNum)
    generateStopNameWithDistanceJson(stopNames,distanceBetweenStopsList,curLinesNum)
    generateStopsWithIDJson(stopNames, curLinesNum)
    generateStopsXml(stopNames,stopOnTheLane, stopStartPos, curLinesNum)
    curLinesNum+=1

    edges = [lane[:-2] for lane in lanes]
    traci.route.add('route1',edges)
    #for edge in edges:
    #    traci.gui.toggleSelection(edge,objType='edge')
    print('done!')
    with open('./testOneLine/visRoute.txt','w') as f:
        f.write(' '.join(edges))
traci.simulation.step()