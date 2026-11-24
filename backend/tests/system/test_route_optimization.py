import pytest

def test_ST04_optimize_route_using_weather_and_vessel_model(calm_route, moderate_route):
    print("Calm distance:", calm_route["optimizedRouteDistance"])
    print("Moderate distance:", moderate_route["optimizedRouteDistance"])

    print("Calm fuel:", calm_route["optimizedRouteFuel"])
    print("Moderate fuel:", moderate_route["optimizedRouteFuel"])

    print("Calm time:", calm_route["optimizedRouteTime"])
    print("Moderate time:", moderate_route["optimizedRouteTime"])

    print("Calm speeds:", [leg["speedKn"] for leg in calm_route["optimizedRouteLegs"][1:]])
    print("Moderate speeds:", [leg["speedKn"] for leg in moderate_route["optimizedRouteLegs"][1:]])

    assert calm_route["optimizedRouteDistance"] > 0
    assert moderate_route["optimizedRouteDistance"] > 0

    assert calm_route["optimizedRouteFuel"] > 0
    assert moderate_route["optimizedRouteFuel"] > 0

    assert calm_route["optimizedRouteTime"] > 0
    assert moderate_route["optimizedRouteTime"] > 0

    calm_speeds = [leg["speedKn"] for leg in calm_route["optimizedRouteLegs"][1:]]

    moderate_speeds = [leg["speedKn"] for leg in moderate_route["optimizedRouteLegs"][1:]]

    assert calm_speeds != moderate_speeds

    for route in (calm_route, moderate_route):
        legs = route["optimizedRouteLegs"]

        assert route["optimizedRouteDistance"] == pytest.approx(sum(leg["distNm"] for leg in legs))
        assert route["optimizedRouteFuel"] == pytest.approx(sum(leg["fuelKg"] for leg in legs))
        assert route["optimizedRouteTime"] == pytest.approx(sum(leg["timeH"] for leg in legs))

def test_ST05_recalculate_route_with_updated_fuel_time_preference(fuel_priority_route, time_priority_route):
    print("Fuel priority distance:", fuel_priority_route["optimizedRouteDistance"])
    print("Time priority distance:", time_priority_route["optimizedRouteDistance"])

    print("Fuel priority fuel:", fuel_priority_route["optimizedRouteFuel"])
    print("Time priority fuel:", time_priority_route["optimizedRouteFuel"])

    print("Fuel priority time:", fuel_priority_route["optimizedRouteTime"])
    print("Time priority time:", time_priority_route["optimizedRouteTime"])

    fuel_speeds = [leg["speedKn"] for leg in fuel_priority_route["optimizedRouteLegs"][1:]]
    time_speeds = [leg["speedKn"] for leg in time_priority_route["optimizedRouteLegs"][1:]]

    print("Fuel priority speeds:", fuel_speeds)
    print("Time priority speeds:", time_speeds)

    assert fuel_priority_route["optimizedRouteDistance"] > 0
    assert time_priority_route["optimizedRouteDistance"] > 0

    assert fuel_priority_route["optimizedRouteFuel"] > 0
    assert time_priority_route["optimizedRouteFuel"] > 0

    assert fuel_priority_route["optimizedRouteTime"] > 0
    assert time_priority_route["optimizedRouteTime"] > 0

    # fuel prioritized route consumes less fuel
    assert(fuel_priority_route["optimizedRouteFuel"] < time_priority_route["optimizedRouteFuel"])

    # time prioritized route takes less time
    assert(time_priority_route["optimizedRouteTime"] < fuel_priority_route["optimizedRouteTime"])

    # optimizer changes its speed selection in response to the updated preference
    assert fuel_speeds != time_speeds



def is_in_storm_region(point):
    lat, lon = point
    return (36.3 <= lat <= 36.6 and -6.96 <= lon <= -6.07)

def test_ST06_recalculate_route_with_updated_wave_height(storm_route, permissive_storm_route):
    print("6m Wave Height Route Distance:", storm_route["optimizedRouteDistance"])
    print("8m Wave Height Route Distance:", permissive_storm_route["optimizedRouteDistance"])

    print("6m Wave Height Route Fuel:", storm_route["optimizedRouteFuel"])
    print("8m Wave Height Route Fuel:", permissive_storm_route["optimizedRouteFuel"])

    print("6m Wave Height Route Time:", storm_route["optimizedRouteTime"])
    print("8m Wave Height Route Time:", permissive_storm_route["optimizedRouteTime"])

    restricted_wave_height_points = [(leg["lat"], leg["lon"]) for leg in storm_route["optimizedRouteLegs"]]
    permissive_wave_height_points = [(leg["lat"], leg["lon"]) for leg in permissive_storm_route["optimizedRouteLegs"]]

    assert storm_route["optimizedRouteDistance"] > 0
    assert permissive_storm_route["optimizedRouteDistance"] > 0

    assert (storm_route["optimizedRouteDistance"] > permissive_storm_route["optimizedRouteDistance"])
    assert (storm_route["optimizedRouteFuel"] > permissive_storm_route["optimizedRouteFuel"])
    assert (storm_route["optimizedRouteTime"] > permissive_storm_route["optimizedRouteTime"])

    assert storm_route["basicRouteUnsafe"] > 0
    assert permissive_storm_route["basicRouteUnsafe"] == 0

    for point in restricted_wave_height_points:
        print("6m Wave Height Point:", point)

    for point in permissive_wave_height_points:
        print("8m Wave Height Point:", point)

    assert restricted_wave_height_points != permissive_wave_height_points

    # restrictive route points (6m or less wave height) avoid the storm region (8m wave height)
    assert not any(is_in_storm_region(point) for point in restricted_wave_height_points)

    # permissive route (allowing 8m wave height) enters the storm region
    assert any(is_in_storm_region(point) for point in permissive_wave_height_points)
    

