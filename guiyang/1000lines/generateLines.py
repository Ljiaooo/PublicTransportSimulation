import traci
import random
import math
import transbigdata as tbd
import sumolib
import requests
import json


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


def getStopName(lon, lat):
    key = 'a501f49646a8dbf082d7cc79b6fe845c'
    lon = round(lon, 6)
    lat = round(lat, 6)
    url = 'https://restapi.amap.com/v3/geocode/regeo?output=json&location={},{}&key={}&radius=1000&extensions=all&batch=false&roadlevel=0'.format(lon,lat,key)
    result = request_url_get(url)
    result = json.loads(result)
    pois = result['regeocode']['pois']
    roads = result['regeocode']['roads']
    if len(pois)>2:
        pois = [pois[i]['name'] for i in range(2)]
    else:
        pois = [pois[i]['name'] for i in range(len(pois))]

    if len(roads)>5:
        roads = [roads[i]['name'] for i in range(5)]
    else:
        roads = [roads[i]['name'] for i in range(len(roads))]
    name_candinates = pois+roads
    return name_candinates[int(len(name_candinates)*random.random())]


def coordinatesTransform(laneID, pos):
    x, y = sumolib.geomhelper.positionAtShapeOffset(net.getLane(laneID).getShape(), pos)
    lon, lat = net.convertXY2LonLat(x, y)
    return lon, lat


def getStopNameAtLane(laneID, pos):
    lon, lat = coordinatesTransform(laneID, pos)
    return getStopName(lon, lat)


def generateStopsXml(stopNames, stopOnTheLane, stopStartPos):
    pass


def generateRouteCSV(Lanes):
    pass


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
    distanceList = []

    stopOnTheLane = []
    stopStartPos = []

    randomStartPoint = getRandomCoord()
    neighborLanes = net.getNeighboringLanes(randomStartPoint, 100)
    while not neighborLanes:
        randomStartPoint = getRandomCoord()
        neighborLanes = net.getNeighboringLanes(randomStartPoint, 100)
    
    #startLaneID
    startLaneID = neighborLanes[0][0].getID()
    lanes.append(startLaneID)
    stopNames.append(getStopNameAtLane(startLaneID,0))
    stopOnTheLane.append(startLaneID)
    stopStartPos.append(0.)

    #get random stops number
    stopNum = getRandomStopNum()

    curStopIndex = 0
    curLane = startLaneID
    satisfied = True
    distanceBetweenStops = 0
    while curStopIndex<stopNum:
        nextLaneInfo = traci.lane.getLinks(curLane)
        if not nextLaneInfo:
            satisfied = False
            break
        nextLaneID = nextLaneInfo[0]
        nextLaneLength = nextLaneInfo[-1]
        curLane = nextLaneID
        curLaneLength = nextLaneLength
        lanes.append(curLane)
        distanceList.append(nextLaneLength)
        distanceBetweenStops+=nextLaneLength
        if distanceBetweenStops>MIN_DISTANCE_BETWEEN_STOPS and nextLaneLength>STOPLENGTH:
            stopNames.append(getStopNameAtLane(curLane,curLaneLength-STOPLENGTH))
            stopOnTheLane.append(curLane)
            stopStartPos.append(curLaneLength-STOPLENGTH)
            distanceBetweenStops = 0
            curStopIndex+=1

    if not satisfied:
        continue






    


    curLinesNum+=1


    




laneID = gui.NEAREST(getRandomCoord())
links = traci.lane.getLinks(laneID)
laneID = links[0][0]


traci.simulation.step()