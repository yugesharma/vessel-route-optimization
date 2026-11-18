import geopandas as gpd
import numpy as np
import shapely
from shapely.ops import transform
from shapely.geometry import shape
from pyproj import Geod, Transformer

geod = Geod(ellps="WGS84")
MERC="+proj=merc +over +datum=WGS84 +units=m"
toWGS=Transformer.from_crs(MERC, "EPSG:4326", always_xy=True)

class NavGrid:
    def __init__(self):
        self.corridorPolygon = None
        self.corridorBoundingBox = None
        self.validNodes = set()
        self.neighborCache = {}
        self.latitudes = None
        self.longitudes = None

    def buildCorridor(self, baseRoute, bufferNm=300):
        routeGeometry = shape(baseRoute["geometry"])
        gdf = gpd.GeoDataFrame(geometry=[routeGeometry], crs="EPSG:4326")
        
        corridorMerc =gdf.to_crs(MERC).buffer(bufferNm*1852).iloc[0]

        self.corridorPolygon = transform(toWGS.transform, corridorMerc)

        return self.corridorPolygon


    def getCorridorBoundingBox(self):
            if self.corridorPolygon is None:
                raise ValueError("Corridor must be built before getting the bounding box")
    
            minlon, minlat, maxlon, maxlat = self.corridorPolygon.bounds
            
            self.corridorBoundingBox = {
                "leftlon": minlon,
                "rightlon": maxlon,
                "toplat": maxlat,
                "bottomlat": minlat,
            }

            return self.corridorBoundingBox

    def buildGrid(self, seaMask, weatherField):
        if not (np.array_equal(seaMask.latitude.values, weatherField.latitude.values)
                and np.array_equal(seaMask.longitude.values, weatherField.longitude.values)):
            raise ValueError("Sea mask and weather grids differ; (row, col) would point at different cells")
        self.latitudes = seaMask.latitude.values
        self.longitudes = seaMask.longitude.values

        lon, lat = np.meshgrid(seaMask.longitude.values, seaMask.latitude.values)
        inCorridor = shapely.contains_xy(self.corridorPolygon, lon, lat)
        hasWaves = weatherField["swh"].notnull().all("step").values

        valid = seaMask.values & inCorridor & hasWaves
        self.validNodes = set(map(tuple, np.argwhere(valid).tolist()))
        self.neighborCache = {}  
        return self.validNodes

    def nodeToCoordinates(self, node):
        row, col = node
        return self.latitudes[row], self.longitudes[col]
    
    def snapToNode(self, point):
        lon, lat = point[0], point[1]
        node = (int(np.abs(self.latitudes - lat).argmin()), int(np.abs(self.longitudes - lon).argmin()))
        if node in self.validNodes:
            return node
        minDistance = float("inf")
        closestNode = None
        for node in self.validNodes:
            lat2, lon2 = self.nodeToCoordinates(node)
            _,_,distance = geod.inv(lon, lat, lon2, lat2)
            if distance < minDistance:
                minDistance = distance
                closestNode = node
        return closestNode
    
    def bearings(self, node1, node2):
        lat1, lon1 = self.nodeToCoordinates(node1)
        lat2, lon2 = self.nodeToCoordinates(node2)
        azimuth, _, _ = geod.inv(lon1, lat1, lon2, lat2)
        return azimuth
    
