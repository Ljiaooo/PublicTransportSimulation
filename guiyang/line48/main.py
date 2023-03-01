import traci
import pandas as pd

sumoBinary = "sumo-gui"
sumoConfig = [sumoBinary, '-c', "./guiyang.sumocfg"]
traci.start(sumoConfig)

up_route = pd.read_csv('./upRoute.csv')['route']
down_route = pd.read_csv('./downRoute.csv')['route']

traci.route.add('048_0',up_route)
traci.route.add('048_1',down_route)

step = 0
while step<1000:
    if step == 0:
        for edge in up_route:
            traci.gui.toggleSelection(edge,'edge')
    if step ==10:
        for edge in down_route:
            traci.gui.toggleSelection(edge,'edge')
        for edge in up_route:
            traci.gui.toggleSelection(edge,'edge')
    traci.simulation.step()
    step+=1