import geopandas as gpd
from shapely.geometry import Point, shape


class NavGrid:
    def __init__(self):
        self.corridorPolygon = None
        self.corridorBoundingBox = None
        self.validNodes = set()

    def buildCorridor(self, baseRoute, bufferNm=300):
        routeGeometry = shape(baseRoute["geometry"])
        gdf = gpd.GeoDataFrame(geometry=[routeGeometry], crs="EPSG:4326")
        gdfMerc = gdf.to_crs("EPSG:3857")

        bufferM = bufferNm * 1852
        corridorMerc = gdfMerc.buffer(bufferM)

        self.corridorPolygon = corridorMerc.to_crs("EPSG:4326").iloc[0]

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

    def buildGrid(self, seaMask):
         
        latitudes = seaMask.latitude.values
        longitudes = seaMask.longitude.values

        for row in range(len(latitudes)):
            for col in range(len(longitudes)):
                lat = latitudes[row]
                lon = longitudes[col]
                isSea = seaMask.values[row, col]
             
                if isSea:
                    point = Point(lon, lat)
                    if self.corridorPolygon.contains(point):
                        self.validNodes.add((row, col))
        return self.validNodes                    
             
