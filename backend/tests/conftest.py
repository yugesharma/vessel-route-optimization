import xarray as xr
import os
from pathlib import Path
import numpy as np
from main import RouteRequest, runRoute
import environmentDataService
import pytest

backendDir=Path(__file__).parent.parent
weatherDataDir=backendDir/'data'/'weatherData'
calmWeatherPath=weatherDataDir/'testData'/'testCalmWeather.nc'
stormWeatherPath=weatherDataDir/'testData'/'testStormWeather.nc'

def build_fake_weather_files():
    calm={"swh": 1.0, "perpw": 8.0, "dirpw": 0.0, "ws": 3.0, "wdir": 0.0}

    if calmWeatherPath.is_file() and stormWeatherPath.is_file():
        print('file already exists')
        return

    realForecasts=sorted(weatherDataDir.glob('weather_*_7day.nc'))
    if not realForecasts:
        raise FileNotFoundError(f"No real forecast in {weatherDataDir}, start the backend once to download it")
    weather_file=realForecasts[-1]

    globalWeather=xr.open_dataset(weather_file)

    globalWeather=globalWeather.assign_coords(valid_time=("step",np.datetime64('2026-01-01T00:00:00')+globalWeather.step.values))
    globalWeather=globalWeather.assign({v:xr.full_like(globalWeather[v],val) for v,val in calm.items()})
    croppedWeather=globalWeather.sel(latitude=slice(43,30),longitude=slice(-13,1))
    calmWeatherPath.parent.mkdir(parents=True, exist_ok=True)
    croppedWeather.to_netcdf(calmWeatherPath)

    croppedWeather['swh'].loc[dict(latitude=slice(36.6,36.3),longitude=slice(-6.96,-6.07))]=8.0
    croppedWeather.to_netcdf(stormWeatherPath)
    print('Fake weather files for testing created')

@pytest.fixture(scope="module")
def calm_route():
    routeRequest=RouteRequest(startPoint=(37.175, -6.981),endPoint=(35.855, -5.336),dateTime='2026-01-01T00:01',fuelTimeWeight=0.5,maxWaveHeight=6.0)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(environmentDataService,"getWeatherForecast",lambda weather_dir:calmWeatherPath)
        return runRoute(routeRequest)

@pytest.fixture(scope="module")
def storm_route():
    routeRequest=RouteRequest(startPoint=(37.175, -6.981),endPoint=(35.855, -5.336),dateTime='2026-01-01T00:01',fuelTimeWeight=0.5,maxWaveHeight=6.0)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(environmentDataService,"getWeatherForecast",lambda weather_dir:stormWeatherPath)
        return runRoute(routeRequest)

if __name__ =="__main__":
    build_fake_weather_files()