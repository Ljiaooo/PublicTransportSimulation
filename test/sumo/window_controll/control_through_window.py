import globalVal
import traci


class ControlFunctions():
    def __init__(self):
        self.globalView = -1
        self.cur = self.globalView


    def changeFocus(self, controllers, to):
        cur = self.cur
        if cur == to:
            return
        if cur!=self.globalView and to!=self.globalView:
            controllers[cur].selectBus(0)
            controllers[cur].selectBus(1)
            controllers[cur].selectRoute(0)
            controllers[cur].selectRoute(1)
            controllers[cur].selectPolygon(0)
            controllers[cur].selectPolygon(1)
            controllers[to].selectBus(0)
            controllers[to].selectBus(1)
            controllers[to].selectRoute(0)
            controllers[to].selectRoute(1)
            controllers[to].selectPolygon(0)
            controllers[to].selectPolygon(1)
        else:
            for i in range(len(controllers)):
                if i!=to:
                    controllers[to].selectBus(0)
                    controllers[to].selectBus(1)
                    controllers[to].selectRoute(0)
                    controllers[to].selectRoute(1)
                    controllers[to].selectPolygon(0)
                    controllers[to].selectPolygon(1)
        self.cur = to

    
    def checkGlobalVals(self, controllers):
        onfocus = globalVal.onfocus
        track_status = globalVal.track_status
        if onfocus != self.cur:
            self.changeFocus(controllers, onfocus)
            if onfocus != self.globalView and track_status:
                traci.gui.track(controllers[onfocus].lastBus)
                traci.gui.setZoom("View #0", 6500.0)
            
        
    def refreshSumoColor(self, controllers):
        if globalVal.onfocus == self.globalView:
            for controller in controllers:
                controller.changePoiColorByPersonNum()
                controller.changeBusColor()
        else:
            controllers[globalVal.onfocus].changePoiColorByPersonNum()
            controllers[globalVal.onfocus].changeBusColor()

        
    def writeData(self, controllers):
        departed_num = 0
        drving_bus = 0
        total_waiting_num = 0
        total_waiting_time = 0
        waiting_num = []
        waiting_time = []
        if self.cur!=self.globalView:
            departed_num = controllers[self.cur].upBusNum
            drving_bus = len(controllers[self.cur].busOnTheRoad)
            total_waiting_num = sum(controllers[self.cur].waitingNum)
            total_waiting_time = sum(controllers[self.cur].waitingTime)
            waiting_num = controllers[self.cur].waitingNum
            waiting_time = controllers[self.cur].waitingTime
            globalVal.data["overview"].apppend(departed_num)
            globalVal.data["overview"].apppend(drving_bus)
            globalVal.data["overview"].apppend(total_waiting_num)
            globalVal.data["overview"].apppend(total_waiting_time)
            globalVal.data["waiting_num"] = waiting_num
            globalVal.data["waiting_time"] = waiting_time
        else:
            for controller in controllers:
                departed_num += controller.upBusNum
                drving_bus += len(controller.busOnTheRoad)
                total_waiting_num += sum(controllers.waitingNum)
                total_waiting_time += sum(controllers.waitingTime)
            globalVal.data["overview"].apppend(departed_num)
            globalVal.data["overview"].apppend(drving_bus)
            globalVal.data["overview"].apppend(total_waiting_num)
            globalVal.data["overview"].apppend(total_waiting_time)


