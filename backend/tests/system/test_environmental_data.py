import pytest
from pathlib import Path
from environmentDataService import EnvironmentDataService
import environmentDataService


def test_ST03_retrieve_consistent_weather_from_saved_forecast(calm_weather_service):
    service = calm_weather_service

    weather = service.weatherAt((0,0),0)

    assert weather["Hs"] == 1.0
    assert weather["Tp"] == 8.0
    assert weather["waveDir"] == 0.0
    assert weather["windSpeed"] == 3.0
    assert weather["windDir"] == 0.0

    weather_again = service.weatherAt((0,0),0)
    assert weather == weather_again