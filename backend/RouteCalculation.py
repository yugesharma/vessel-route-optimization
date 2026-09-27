import searoute
from classes.route import Route
from classes.navGrid import NavGrid
from classes.vessel import vsl
from environmentDataService import EnvironmentDataService
from geographicDataService import GeographicDataService
from calmWaterResistance import calmWaterResistance
from waveAddedResistance import waveAddedResistance

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

    print('start wave height:', startWeather["swh"].values)
    print('end wave height:', endWeather["swh"].values)

    # print(bbox)
    # print(environmentDataService.weatherField)
    # print(geographicDataService.seaMask)
    # print("Valid nodes:", len(navGrid.validNodes))

def calculateRoute(startPoint, endPoint, dateTime):
    setup(startPoint, endPoint)


    


