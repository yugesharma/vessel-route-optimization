import searoute
from classes import Route


def calculateRoute(startPoint, endPoint):
    route = Route(startPoint, endPoint)
    route.getBaseRoute()
    bbox = route.getCorridorBoundingBox()
    print(bbox)
    return route