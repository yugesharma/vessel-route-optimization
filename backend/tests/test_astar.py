import numpy as np
from classes.navGrid import NavGrid
from RouteCalculation import legCost, aStar
from classes.vessel import Vessel, SternShape

class FakeWeather:
    def __init__(self, badWeatherNodes):
        self.badWeatherNodes = badWeatherNodes

    def weatherAt(self, node, time):
        if node in self.badWeatherNodes:
            return {"Hs": 15, "Tp": 10, "waveDir": 90, "windSpeed": 0, "windDir": 0}
        return {"Hs": 0, "Tp": 0, "waveDir": 0, "windSpeed": 0, "windDir": 0}

def run_astar(start,goal,badWeatherNodes,n=7):
    navGrid = NavGrid()
    navGrid.latitudes=1-np.arange(n)*0.25
    navGrid.longitudes=np.arange(n)*0.25
    navGrid.validNodes=set(map(tuple, np.argwhere(np.ones((n,n))).tolist()))

    speeds=[6,8,12]
    weather = FakeWeather(badWeatherNodes)
    testVessel = Vessel(
    L=205.0, B=32.0, draft=10, TF=10, TA=10,  
    CB=37500/205/32/10, CM=0.980, lcb=-0.75,
    CWP=0.750, 
    ABT=20, hB=4,  
    AT=16,  
    Cstern=SternShape.U_SHAPED_HOGNER,
    #below values not in the original paper, but are needed for the calculation
    kyy=0.25,
    LE=60.0,  
    eta=0.70,  
    sfoc=175.0,  
    mcrKw=27000.0,  
)

    costMin=min(legCost(1, testVessel.calmWaterFuelPerNM(speed), 1/speed, 1, 0.5, 600.0, 1700.0)
                for speed in speeds)
    
    key,_,parents=aStar(start,goal,0,testVessel,speeds,navGrid,weather,costMin,1,1,0.5,600.0,1700.0)
    path=[]
    while key is not None:
        path.append(key[0])
        key=parents[key] and parents[key][0]

    return path[::-1]

def test_astar():
    badWeatherNodes={(2,2),(2,3),(2,4),(3,2),(3,3),(3,4),(3,5),(4,2),(4,3),(4,4)}
    badWeatherPath=run_astar((3,0),(3,6),badWeatherNodes)
    print("badWeatherPath:",badWeatherPath)
    assert not set(badWeatherPath) & badWeatherNodes
    calmWeatherPath=run_astar((3,0),(3,6),set())
    print("calmWeatherPath:",calmWeatherPath)
    assert all(i==3 for (i,_) in calmWeatherPath)

if __name__ == "__main__":
    test_astar()
        