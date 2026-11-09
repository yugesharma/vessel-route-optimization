import xarray as xr
from pathlib import Path
from pyproj import Geod
from itertools import pairwise

def test_calm_weather_route(calm_route):
    assert len(calm_route["optimizedRouteLegs"])>1
    assert calm_route["optimizedRouteDistance"]>0


def test_ST01_calculate_route_with_two_ocean_coordinates(calm_route):

    # verify route generation
    assert len(calm_route["optimizedRouteLegs"]) > 1

    # verify positive distance
    assert calm_route["optimizedRouteDistance"] > 0

    # verify starting point
    first_leg = calm_route["optimizedRouteLegs"][0]
    assert abs(first_leg["lat"] - 37.175) <= 0.25
    assert abs(first_leg["lon"] - (-6.981)) <= 0.25

    # verify ending point
    last_leg = calm_route["optimizedRouteLegs"][-1]
    assert abs(last_leg["lat"] - 35.855) <= 0.25
    assert abs(last_leg["lon"] - (-5.336)) <= 0.25

def test_ST02_generate_route_avoiding_land(land_avoidance_route):
    # list of coords on optimized route
    legs = land_avoidance_route["optimizedRouteLegs"]

    sea_mask_path = (Path(__file__).parents[2] / "data" / "geographicData" /"sea_mask_0.25deg.nc")
    sea_mask = xr.open_dataarray(sea_mask_path)

    # check every coord in the optimized route is water
    for leg in legs:
        cell = sea_mask.sel(latitude=leg["lat"], longitude=leg["lon"], method="nearest")
        assert bool(cell.item())

    # verify that every segment between consecutive points avoids land
    geod = Geod(ellps="WGS84")
    for start, end in pairwise(legs):
        points = geod.npts(start["lon"], start["lat"], end["lon"], end["lat"], 10)
        for lon, lat in points:
            cell = sea_mask.sel(latitude=lat, longitude=lon, method="nearest")
            assert bool(cell.item()), f"Point ({lat}, {lon}) is on land"

    # verify the direct path crosses land so that this is a valid land-avoidance scenario
    direct_points = geod.npts(-6.8, 36.6, -4.4, 36.5, 20)
    land_count = 0
    
    for lon,lat in direct_points:
        cell = sea_mask.sel(latitude=lat, longitude=lon, method="nearest")
        
        if not bool(cell.item()):
            land_count +=1
        
    assert land_count > 0, "Direct route does not cross land"

