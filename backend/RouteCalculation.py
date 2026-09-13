import searoute
from classes import Route


def calculateRoute(startPoint, endPoint):
    route = Route(startPoint, endPoint)
    route.getBaseRoute()
    return route