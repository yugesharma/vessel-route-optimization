from classes.navGrid import NavGrid
from classes.route import Route
from environmentDataService import EnvironmentDataService
from geographicDataService import GeographicDataService
from waveAddedResistance import buildT
import numpy as np
from classes.vessel import vsl

def getBaseRoute(startPoint, endPoint):
    route = Route(startPoint, endPoint)
    route.getBaseRoute()
    return route.baseRoute


def setup(baseRoute,startPoint, endPoint,dateTime,speeds,distanceWeight,fuelTimeWeight,timeBinSize,priceFuel,priceTime):
    vsl.waveResistanceTable,vsl.ALPHA=buildT(vsl)
    navGrid = NavGrid()
    navGrid.buildCorridor(baseRoute)
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

    t0=(np.datetime64(dateTime) - environmentDataService.getCycleStart()) / np.timedelta64(1, "h")

    return navGrid, environmentDataService, startNode, endNode, t0
