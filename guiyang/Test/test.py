from tracemalloc import stop
import traci





traci.start(['sumo-gui','-c','guiyang.sumocfg'])


#add a person at 47_0(the first stop in stop_47.add.xml)
#append waiting stage for 10s
traci.person.add("testPerson",edgeID='593486825#3',pos=150.0)
traci.person.appendWalkingStage("testPerson",'593486825#3',150.0,stopID='47_0')
traci.person.appendDrivingStage("testPerson",'593486825#3',lines='47')


#print(traci.busstop.getPersonCount('47_0'))

step = 0
while step < 1000:
    traci.simulation.step()
    if step == 5:
        #print the person count at stop_47 
        #the print result is 0 (where is the problem?)
        print(traci.busstop.getPersonCount('47_0'))
        print(traci.person.getWaitingTime('testPerson'))
        traci.gui.toggleSelection("test_bus")
    


    step += 1


