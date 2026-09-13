from enum import IntEnum
import searoute as sr


class SternShape(IntEnum):
    PRAM_WITH_GONDOLA = -25
    V_SHAPED = -10
    NORMAL = 0
    U_SHAPED_HOGNER = 10


class Vessel:
    def __init__(self, L, B, draft, TF, CM, CB, CWP, ABT, hB, AT, lcb, Cstern=SternShape.NORMAL):
        self.L = L
        self.B = B
        self.draft = draft
        self.TF = TF
        self.CM = CM
        self.CB = CB
        self.CWP = CWP
        self.ABT = ABT
        self.hB = hB
        self.AT = AT
        self.lcb = lcb
        self.Cstern = Cstern
        self.CP = 0
        self.displacement = 0
        self.wettedSurfaceArea = 0

    def getCP(self):
        self.CP = self.CB / self.CM
        return self.CP

    def getDisplacement(self):
        self.displacement = self.CB * self.L * self.B * self.draft
        return self.displacement

    def getWettedSurfaceArea(self):
        self.wettedSurfaceArea = (
            self.L * (2 * self.draft + self.B) * self.CM**0.5
            * (0.453 + 0.4425 * self.CB - 0.2862 * self.CM
               - 0.003467 * (self.B / self.draft) + 0.3696 * self.CWP)
            + 2.38 * self.ABT / self.CB
        )
        return self.wettedSurfaceArea


class Route:
    def __init__(self, startPoint, endPoint):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.baseRoute = []
        self.optimizedRute = []
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


    