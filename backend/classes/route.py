import searoute as sr


class Route:
    def __init__(self, startPoint, endPoint):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.baseRoute = []
        self.distance = 0
        self.averageSpeed = 0
        self.totalFuel=0
        self.distanceWeight=0
        self.waveWeight=0
        self.windWeight=0

    def getStartPoint(self):
        return self.startPoint

    def getEndPoint(self):
        return self.endPoint
    
    def getBaseRoute(self):
        route = sr.searoute(self.startPoint, self.endPoint, speed_knot=12.5, units="naut")
        self.baseRoute = route
        return self.baseRoute

    