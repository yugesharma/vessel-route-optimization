import searoute
from classes.route import Route
from classes.navGrid import NavGrid
from environmentDataService import EnvironmentDataService
from geographicDataService import GeographicDataService


def calculateRoute(startPoint, endPoint):
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

    # build valid navigation grid with nodes that are within the corridor and over sea
    navGrid.buildGrid(geographicDataService.seaMask)

    
    print(bbox)
    print(environmentDataService.weatherField)
    print(geographicDataService.seaMask)
    print("Valid nodes:", len(navGrid.validNodes))

    return route