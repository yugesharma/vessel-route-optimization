import searoute
from classes.route import Route
from classes.navGrid import NavGrid
from classes.vessel import vsl
from environmentDataService import EnvironmentDataService
from geographicDataService import GeographicDataService
from pyproj import Geod

geod = Geod(ellps="WGS84")

def setup(startPoint, endPoint):
    route = Route(startPoint, endPoint)
    route.getBaseRoute()
    
    navGrid = NavGrid()
    navGrid.buildCorridor(route.baseRoute)
    bbox = navGrid.getCorridorBoundingBox()

    # cropped weather data for the route corridor
    environmentDataService = EnvironmentDataService()
    environmentDataService.getWeatherData(bbox)

    # cropped land/water mask for the route corridor
    geographicDataService = GeographicDataService()
    geographicDataService.getSeaMask(bbox)

    # build valid navigation grid: nodes inside the corridor, over sea, with wave data
    navGrid.buildGrid(geographicDataService.seaMask, environmentDataService.weatherField)

    startNode = navGrid.snapToNode(startPoint)
    endNode = navGrid.snapToNode(endPoint)

    startWeather = environmentDataService.weatherAt(startNode, 0)
    endWeather = environmentDataService.weatherAt(endNode, 0)

    print('start wave height:', startWeather["Hs"])
    print('end wave height:', endWeather["Hs"])

    # print(bbox)
    # print(environmentDataService.weatherField)
    # print(geographicDataService.seaMask)
    # print("Valid nodes:", len(navGrid.validNodes))

    return navGrid, environmentDataService, startNode, endNode

def calculateRoute(startPoint, endPoint, dateTime, distanceWeight, windWeight, waveWeight):
    setup(startPoint, endPoint)


def neighbors(node, departureTime,navGrid,speeds):
    lat1, lon1 = navGrid.nodeToCoordinates(node)

    validNeighbors=[]
    for dr, dc in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
        idx=(node[0]+dr,node[1]+dc)
        if idx not in navGrid.validNodes:
            continue
        # diagonal: both side cells must be valid, so the leg can't cut a land corner
        if dr and dc and ((node[0]+dr,node[1]) not in navGrid.validNodes
                          or (node[0],node[1]+dc) not in navGrid.validNodes):
            continue
        lat2, lon2 = navGrid.nodeToCoordinates(idx)
        azimuth,_,distanceM = geod.inv(lon1,lat1,lon2,lat2)
        validNeighbors.append((idx,distanceM/1852,azimuth))  # distance in nm, heading in deg true
    
    legalMoves=[]
    for neighbor,distance,heading in validNeighbors:
        for speed in speeds:
            timeH=distance/speed
            arrivalTime=departureTime+timeH
            legalMoves.append((neighbor,speed,heading,distance,timeH,arrivalTime))

    return legalMoves

def edgeCost(node,move,departureTime,vsl,environmentDataService,distanceWeight=1.0,fuelWeight=1.0,timeWeight=1.0):
    neighbor,speed,heading,distance,timeH,arrivalTime=move
    weather=environmentDataService.weatherAt(node,departureTime)
    fuel=vsl.legFuel(speed,heading,timeH,weather)
    if fuel is None:
        return None  # speed not achievable in this weather (needs more than MCR)
    cost=distanceWeight*distance+fuelWeight*fuel+timeWeight*timeH
    return cost
