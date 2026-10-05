import searoute
from classes.route import Route
from classes.navGrid import NavGrid
from classes.vessel import vsl
from environmentDataService import EnvironmentDataService
from geographicDataService import GeographicDataService
from pyproj import Geod
from math import floor
import heapq
import numpy as np
import time

geod = Geod(ellps="WGS84")

def setup(startPoint, endPoint,dateTime,speeds,distanceWeight,fuelTimeWeight,timeBinSize,priceFuel,priceTime):
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
    overlayPath, overlayBounds = environmentDataService.createWeatherOverlay(0)
    
    print("Overlay bounds:", overlayBounds)


    # build valid navigation grid: nodes inside the corridor, over sea, with wave data
    navGrid.buildGrid(geographicDataService.seaMask, environmentDataService.weatherField)

    startNode = navGrid.snapToNode(startPoint)
    endNode = navGrid.snapToNode(endPoint)

    startWeather = environmentDataService.weatherAt(startNode, 0)
    endWeather = environmentDataService.weatherAt(endNode, 0)

    t0=(np.datetime64(dateTime) - environmentDataService.getCycleStart()) / np.timedelta64(1, "h")

    # cheapest possible cost per nm: calm water (legFuel never goes below it), same formula as edgeCost
    costMin=min(legCost(1, vsl.calmWaterFuelPerNM(speed), 1/speed, distanceWeight, fuelTimeWeight, priceFuel, priceTime)
                for speed in speeds)


    print('start wave height:', startWeather["Hs"])
    print('end wave height:', endWeather["Hs"])

    # print(bbox)
    # print(environmentDataService.weatherField)
    # print(geographicDataService.seaMask)
    # print("Valid nodes:", len(navGrid.validNodes))


    return route, navGrid, environmentDataService, startNode, endNode, t0, costMin, overlayPath, overlayBounds

# default prices: VLSFO ~600 $/t, VLCC time charter ~40k $/day (~1700 $/h)
def calculateRoute(startPoint, endPoint, dateTime, distanceWeight=1.0, fuelTimeWeight=0.5, priceFuel=600.0, priceTime=1700.0, onProgress=None):
    speeds=[6,8,10,12,14]
    timeBinSize=3
    start_time = time.time()
    route, navGrid, environmentDataService, startNode, endNode, t0, costMin, overlayPath, overlayBounds = setup(
        startPoint, endPoint, dateTime, speeds, distanceWeight=distanceWeight, fuelTimeWeight=fuelTimeWeight,
        timeBinSize=timeBinSize, priceFuel=priceFuel, priceTime=priceTime)
    end_time = time.time()
    print(f"Time taken to setup: {end_time - start_time} seconds")

    start_time = time.time()
    goalKey, g, parents = aStar(startNode, endNode, t0, vsl, speeds, navGrid, environmentDataService,
                                costMin, timeBinSize, distanceWeight=distanceWeight, fuelTimeWeight=fuelTimeWeight,
                                priceFuel=priceFuel, priceTime=priceTime, onProgress=onProgress)
    end_time = time.time()
    print(f"Time taken to calculate route: {end_time - start_time} seconds")
    if goalKey is None:
        return route, None, overlayPath, overlayBounds
    return route, reconstructPath(parents, goalKey, navGrid, t0), overlayPath, overlayBounds


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

def legCost(distanceNm, fuelKg, timeH, distanceWeight, fuelTimeWeight, priceFuel, priceTime):
    # priceFuel in $/tonne, priceTime in $/hour; shared by edgeCost and the heuristic so they can't drift apart
    return distanceWeight*distanceNm + fuelTimeWeight*fuelKg/1000*priceFuel + (1-fuelTimeWeight)*timeH*priceTime

def edgeCost(node,move,departureTime,vsl,environmentDataService,distanceWeight,fuelTimeWeight,priceFuel,priceTime):
    neighbor,speed,heading,distance,timeH,arrivalTime=move
    weather=environmentDataService.weatherAt(node,departureTime)
    fuel=vsl.legFuel(speed,heading,timeH,weather)
    if fuel is None:
        return None  # speed not achievable in this weather (needs more than MCR)
    return legCost(distance, fuel, timeH, distanceWeight, fuelTimeWeight, priceFuel, priceTime),fuel

def timeBin(t0, t, binSize):
    return floor((t-t0)/binSize)

def heuristic(node,goal,navGrid,costMin):
    lat1, lon1 = navGrid.nodeToCoordinates(node)
    lat2, lon2 = navGrid.nodeToCoordinates(goal)
    _,_,distanceM = geod.inv(lon1,lat1,lon2,lat2)
    distanceNm = distanceM / 1852
    return distanceNm*costMin

def aStar(start,goal,t0,vsl,speeds,navGrid,environmentDataService,costMin,timeBinSize,distanceWeight,fuelTimeWeight,priceFuel,priceTime,onProgress=None):
    bestCost={}
    bestCost[(start,0)]=0
    parents={}
    parents[(start,0)]=None  # parent is a tuple (currKey,speed,heading,distance,timeH,arrivalTime,g2,fuel)
    g=0
    h=heuristic(start,goal,navGrid,costMin)
    f=g+h
    openList=[(f,0,g,h,start,t0)]
    heapq.heapify(openList)
    exploredNodes=[]
    sentCells=set()  
    expanded=0
    webSocketFrequency = 5

    while openList:
        f,counter,g,h,currentNode,depTime = heapq.heappop(openList)
        if currentNode not in sentCells:
            sentCells.add(currentNode)
            exploredNodes.append([float(c) for c in navGrid.nodeToCoordinates(currentNode)])
        expanded+=1
        if expanded%1000==0 and webSocketFrequency < 100:
            webSocketFrequency = webSocketFrequency * 2
        if onProgress and exploredNodes and expanded % webSocketFrequency == 0:
            onProgress({"exploredNodes": exploredNodes,
                        })
            exploredNodes=[]
        currKey=(currentNode,timeBin(t0,depTime,timeBinSize))

        if currKey in bestCost and g > bestCost[currKey]:
            continue

        if currentNode == goal:
            return currKey,g,parents
        moves=neighbors(currentNode,depTime,navGrid,speeds)
        for move in moves:
            nextNode,speed,heading,distance,timeH,arrivalTime=move
            result = edgeCost(currentNode,move,depTime,vsl,environmentDataService,distanceWeight=distanceWeight,
                              fuelTimeWeight=fuelTimeWeight,priceFuel=priceFuel,priceTime=priceTime)
            if result is None:
                continue
            cost,fuel=result
            g2 =g+ cost
            key2=(nextNode,timeBin(t0,arrivalTime,timeBinSize))

            if key2 not in bestCost or g2 < bestCost[key2]:
                bestCost[key2]=g2
                
                parents[key2]=(currKey,speed,heading,distance,timeH,arrivalTime,g2,fuel)
                h2=heuristic(nextNode,goal,navGrid,costMin)
                f2=g2+h2
                heapq.heappush(openList,(f2,counter+1,g2,h2,nextNode,arrivalTime))
    return None,None,None

def reconstructPath(parents, goalKey, navGrid, t0):
    # walk parent records from the goal back to the start, then reverse
    legs=[]
    key=goalKey
    while parents[key] is not None:
        prevKey,speed,heading,distance,timeH,arrivalTime,g,fuel=parents[key]
        lat,lon=navGrid.nodeToCoordinates(key[0])
        legs.append({"lat":float(lat),"lon":float(lon),"speedKn":speed,"headingDeg":heading,
                     "arrivalTime":arrivalTime,"distNm":distance,"timeH":timeH,"fuelKg":fuel})
        key=prevKey
    # start point: no leg led here, so zero distance/time/fuel
    lat,lon=navGrid.nodeToCoordinates(key[0])
    legs.append({"lat":float(lat),"lon":float(lon),"speedKn":None,"headingDeg":None,
                 "arrivalTime":t0,"distNm":0.0,"timeH":0.0,"fuelKg":0.0})
    legs.reverse()
    return legs

