import traci
from sumo_controller import SumoController
from simulation.passengerflow import PassengerFlow
from simulation.bus_controller import BusController
from simulation.utils import str2seconds


if __name__ == '__main__':
    sumoBinary = "sumo-gui"
    sumoConfig = [sumoBinary, '-c', "./guiyang.sumocfg"]
    traci.start(sumoConfig)


    route = 17
    #route = 480
    step = 0
    sumo_controller = SumoController(route)



    sumo_controller.drawStopPoi()
    sumo_controller.selectRoute(0)
    sumo_controller.selectRoute(1)
    while(step<100000):
        sumo_controller.updateBusLists()
        #add persons
        if step%60==0:
            for i in range(sumo_controller.upStopNum):
                sumo_controller.addPassenger('{}_0_{}'.format(str(route).zfill(3), str(i).zfill(2)),0)
                sumo_controller.addPassenger('{}_1_{}'.format(str(route).zfill(3), str(i).zfill(2)),1)

        if step%600==0:
            sumo_controller.addBus(0)
            sumo_controller.addBus(1)



        sumo_controller.changeBusColor()
        sumo_controller.changePoiColorByPersonNum()
        traci.simulation.step()
        step+=1

