import xarray as xr
import os
from pathlib import Path
import numpy as np
from main import runRoute
import pytest
import environmentDataService

def build_fake_weather_files():
    try:
        calm={"swh": 1.0, "perpw": 8.0, "dirpw": 0.0, "ws": 3.0, "wdir": 0.0}
        
        current_dir=Path.cwd()
        weatherDataDir=current_dir.parent/'data'/'weatherData'
        calmWeatherPath=weatherDataDir/'testData'/'testCalmWeather.nc'
        stormWeatherPath=weatherDataDir/'testData'/'testStormWeather.nc'

        if not calmWeatherPath.is_file():
            for file_path in weatherDataDir.rglob('*.nc'):
                weather_file=file_path
                continue
            
            globalWeather=xr.open_dataset(weather_file)
        
            globalWeather=globalWeather.assign_coords(valid_time=("step",np.datetime64('2026-01-01T00:00:00')+globalWeather.step.values))
            globalWeather=globalWeather.assign({v:xr.full_like(globalWeather[v],val) for v,val in calm.items()})
            croppedWeather=globalWeather.sel(latitude=slice(37.4263,35.5651),longitude=slice(-7.6849,-4.6717))
            croppedWeather.to_netcdf(calmWeatherPath)

            croppedWeather['swh'].loc[dict(latitude=slice(36.6,36.3),longitude=slice(-6.96,-6.07))]=8.0
            croppedWeather.to_netcdf(stormWeatherPath)
            print('Fake weather files for testing created')
        else:
            print('file already exists')

    except Exception as e:
        print('error: ',e)



if __name__ =="__main__":
    build_fake_weather_files()