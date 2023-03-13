import traci
from sumo_controller import SumoController
from simulation.passengerflow import PassengerFlow
from simulation.bus_controller import BusController
from simulation.utils import str2seconds


if __name__ == '__main__':
    sumoBinary = "sumo-gui"
    sumoConfig = [sumoBinary, '-c', "./guiyang.sumocfg"]
    traci.start(sumoConfig)

#27
    route = 27
    #route = 480
    step = 0
    controllers = []
    for i in range(1000):
        sumo_controller = SumoController(route)
        sumo_controller.drawStopPoi()
        sumo_controller.selectRoute(0)
        sumo_controller.selectRoute(1)
        controllers.append(sumo_controller)



    print(traci.lane.getLinks('475686362#1_1'))
    while(step<100000):
        for i in range(1000):
            controllers[i].updateBusLists()
        #add persons
        if step%60==0:
            for k in range(1000):
                for i in range(controllers[k].upStopNum):
                    controllers[k].addPassenger('{}_0_{}'.format(str(route).zfill(3), str(i).zfill(2)),0)
                    controllers[k].addPassenger('{}_1_{}'.format(str(route).zfill(3), str(i).zfill(2)),1)

        if step%600==0:
            for i in range(1000):
                controllers[i].addBus(0)
                controllers[i].addBus(1)



        for i in range(1000):
            controllers[i].changeBusColor()
            controllers[i].changePoiColorByPersonNum()
        traci.simulation.step()
        step+=1

