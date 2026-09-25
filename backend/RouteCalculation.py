import searoute
from classes.route import Route
from environmentDataService import EnvironmentDataService
from geographicDataService import GeographicDataService


def calculateRoute(startPoint, endPoint):
    route = Route(startPoint, endPoint)
    route.getBaseRoute()
    bbox = route.getCorridorBoundingBox()

    # cropped weather data for the route corridor
    environmentDataService = EnvironmentDataService()
    environmentDataService.getWeatherData(bbox)

    # cropped land/water mask for the route corridor
    geographicDataService = GeographicDataService()
    geographicDataService.getSeaMask(bbox)

    
    print(bbox)
    print(environmentDataService.weatherField)
    print(geographicDataService.seaMask)

    return route