import traci
from sumo_controller import SumoController
from simulation.passengerflow import PassengerFlow
from simulation.bus_controller import BusController
from simulation.utils import str2seconds


if __name__ == '__main__':
    sumoBinary = "sumo-gui"
    sumoConfig = [sumoBinary, '-c', "./guiyang.sumocfg"]
    traci.start(sumoConfig)

    route = 1
    step = 0
    base_time = '06:29:50'
    start_time_stamp = str2seconds(base_time)
    sumo_controller = SumoController(route)
    upPassengerflow = PassengerFlow(start_time_stamp, "_"+str(route), "up","0000", sumo_controller)
    upBusController = BusController(start_time_stamp, "_"+str(route), "up","0000", sumo_controller)
    downPassengerflow = PassengerFlow(start_time_stamp, "_"+str(route), "down","0000", sumo_controller)
    downBusController = BusController(start_time_stamp, "_"+str(route), "down","0000", sumo_controller)
    upBusController.set_passengerflow(upPassengerflow)
    downBusController.set_passengerflow(downPassengerflow)



    sumo_controller.drawStopPoi()
    sumo_controller.selectRoute(0)
    sumo_controller.selectRoute(1)
    while(step<100000):
        if step==500:
            print(traci.vehicle.getStops('bus001_1_00'))
        sumo_controller.updataBusLists()
        upPassengerflow.sumo_update()
        downPassengerflow.sumo_update()
        upBusController.sumo_update()
        downBusController.sumo_update()

        sumo_controller.changeBusColor()
        sumo_controller.changePoiColorByPersonNum()
        traci.simulation.step()
        step+=1

