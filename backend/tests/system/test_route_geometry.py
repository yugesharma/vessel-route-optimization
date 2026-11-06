def test_calm_weather_route(calm_route):
    assert len(calm_route["optimizedRouteLegs"])>1
    assert calm_route["optimizedRouteDistance"]>0

