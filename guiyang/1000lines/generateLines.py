import traci
import random
import math
import transbigdata as tbd
import sumolib


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

#25~35站点数量
LINESDEMAND = 1
MINSTOPINTERVAL = 600
MINSTOPNUM = 25
MAXSTOPNUM = 35

curLinesNum = 0

##data to write: stop names, 
#while curLinesNum < LINESDEMAND:
#    randomStartPoint = getRandomCoord()
#    neighborLanes = net.getNeighboringLanes(randomStartPoint, 100)
#    while not neighborLanes:
#        randomStartPoint = getRandomCoord()
#        neighborLanes = net.getNeighboringLanes(randomStartPoint, 100)
#    
#    #startLaneID
#    startLaneID = neighborLanes[0][0].getID()
#
#
#
#    
#
#
#    curLinesNum+=1
#
#
#    
#
#
#
#
#laneID = gui.NEAREST(getRandomCoord())
#links = traci.lane.getLinks(laneID)
#laneID = links[0][0]
#

traci.simulation.step()