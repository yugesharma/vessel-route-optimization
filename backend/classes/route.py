import geopandas as gpd
import searoute as sr
from shapely.geometry import Point, shape

class Route:
    def __init__(self, startPoint, endPoint):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.baseRoute = []
        self.corridorPolygon = None
        self.corridorBoundingBox = {}
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

    def getCorridorPolygon(self, bufferNm=300):
        if not self.baseRoute:
            self.getBaseRoute()

        routeGeometry = shape(self.baseRoute["geometry"])
        gdf = gpd.GeoDataFrame(geometry=[routeGeometry], crs="EPSG:4326")
        gdfMerc = gdf.to_crs("EPSG:3857")

        bufferM = bufferNm * 1852
        corridorMerc = gdfMerc.buffer(bufferM)

        self.corridorPolygon = corridorMerc.to_crs("EPSG:4326").iloc[0]
        return self.corridorPolygon

    def getCorridorBoundingBox(self):
        if self.corridorPolygon is None:
            self.getCorridorPolygon()

        minlon, minlat, maxlon, maxlat = self.corridorPolygon.bounds
        self.corridorBoundingBox = {
            "leftlon": minlon,
            "rightlon": maxlon,
            "toplat": maxlat,
            "bottomlat": minlat,
        }
        return self.corridorBoundingBox

    def isInsideCorridor(self, lon, lat):
        if self.corridorPolygon is None:
            self.getCorridorPolygon()
        return self.corridorPolygon.contains(Point(lon, lat))
