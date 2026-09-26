import os
import glob
import requests
from datetime import date
import xarray as xr
from cfgrib.xarray_store import open_datasets
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATE_STRING = date.today().strftime("%Y%m%d")
FORECAST_HOURS = list(range(0, 7 * 24 + 1, 3))  

class EnvironmentDataService:
    def __init__(self):
        self.weatherField = None
        self.validHours = None

    def getWeatherData(self, bbox):
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        weather_dir = os.path.join(data_dir, "weatherData")

        os.makedirs(weather_dir, exist_ok=True)

        weather_file = getWeatherForecast(weather_dir)
        globalWeather = xr.open_dataset(weather_file)

        self.cropWeather(globalWeather, bbox)

    def cropWeather(self, globalWeather, bbox):
        croppedWeather = globalWeather.sel(
            latitude=slice(bbox["toplat"], bbox["bottomlat"]),
            longitude=slice(bbox["leftlon"], bbox["rightlon"])
            )

        self.weatherField = croppedWeather
        self.validHours = croppedWeather.valid_time.values
        return self.weatherField, self.validHours

    


def downloadWaveData():
    url = (
        "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_wave_0p25.pl"
        f"?dir=%2Fgefs.{DATE_STRING}%2F00%2Fwave%2Fgridded"
        "&file=gefs.wave.t00z.c00.global.0p25.f000.grib2"
        "&var_HTSGW=on&lev_surface=on"
    )
    response = requests.get(url, timeout=120)
    if response.status_code != 200 or not response.content.startswith(b"GRIB"):
        raise RuntimeError(f"Failed to download wave data: HTTP {response.status_code}")
    print("Wave data downloaded successfully")
    return response


def downloadWeatherData(weather_dir: str) -> list[str]:
    steps_dir = os.path.join(weather_dir, f"steps_{DATE_STRING}")
    os.makedirs(steps_dir, exist_ok=True)

    step_files = []
    with requests.Session() as session:
        for fh in FORECAST_HOURS:
            out_path = os.path.join(steps_dir, f"weather_f{fh:03d}.grib2")
            if os.path.exists(out_path):
                with open(out_path, "rb") as existing:
                    if existing.read(4) == b"GRIB":
                        print(f"Skipping existing f{fh:03d}")
                        step_files.append(out_path)
                        continue

            url = (
                "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_wave_0p25.pl"
                f"?dir=%2Fgefs.{DATE_STRING}%2F00%2Fwave%2Fgridded"
                f"&file=gefs.wave.t00z.c00.global.0p25.f{fh:03d}.grib2"
                "&var_SWDIR=on&var_SWELL=on&var_SWPER=on"
                "&var_WDIR=on&var_WIND=on&var_WVDIR=on&var_WVHGT=on&var_WVPER=on&lev_surface=on"
            )
            response = session.get(url, timeout=120)
            if response.status_code != 200 or not response.content.startswith(b"GRIB"):
                raise RuntimeError(
                    f"Failed to download weather f{fh:03d}: HTTP {response.status_code}"
                )
            with open(out_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded weather f{fh:03d}")
            step_files.append(out_path)
    return step_files


def saveData(response, file_name, file_dir):
    os.makedirs(file_dir, exist_ok=True)
    out_path = os.path.join(file_dir, f"{file_name}_{DATE_STRING}.grib2")
    with open(out_path, "wb") as f:
        f.write(response.content)
    print(f"{file_name} data saved to {out_path}")
    return out_path


def combineWeatherForecast(step_files: list[str], weather_dir: str) -> str:
    datasets = []
    for path in step_files:
        for stale in glob.glob(f"{path}.*.idx"):
            os.remove(stale)
        ds = open_datasets(path)[0]
        if "step" in ds.coords and "step" not in ds.dims:
            ds = ds.expand_dims("step")
        datasets.append(ds)

    combined = xr.concat(datasets, dim="step").sortby("step")
    new_lon = ((combined.longitude + 180) % 360) - 180
    combined = combined.assign_coords(longitude=new_lon)
    combined = combined.sortby("longitude")
    
    
    if "surface" in combined.coords:
        combined = combined.drop_vars("surface")

    out_path = os.path.join(weather_dir, f"weather_{DATE_STRING}_7day.nc")
    combined.to_netcdf(
        out_path,
        encoding={var: {"zlib": True, "complevel": 4} for var in combined.data_vars},
    )
    print(f"Combined {len(step_files)} steps into {out_path}")

    for ds in datasets:
        ds.close()
    combined.close()
    return out_path


def getWeatherForecast(weather_dir: str) -> str:
    out_path = os.path.join(weather_dir, f"weather_{DATE_STRING}_7day.nc")
    if os.path.exists(out_path):
        print(f"Weather forecast already exists for {DATE_STRING}")
        return out_path
    return combineWeatherForecast(downloadWeatherData(weather_dir), weather_dir)


def convertGribToPng(gribFile):
    for stale in glob.glob(f"{gribFile}.*.idx"):
        os.remove(stale)
    ds = xr.open_dataset(gribFile, engine="cfgrib")
    data = ds["swh"]

    wavepngsDir = os.path.join(os.path.dirname(__file__), "data", "wavepngs")
    os.makedirs(wavepngsDir, exist_ok=True)
    out_path = os.path.join(wavepngsDir, f"wave_{DATE_STRING}.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    mesh = ax.pcolormesh(
        data.longitude, data.latitude, data.values, cmap="turbo", shading="auto"
    )
    fig.colorbar(mesh, ax=ax, label="swh (m)")
    ax.set_title(f"Significant Wave Height - {DATE_STRING}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    ds.close()
    print(f"Wave map saved to {out_path}")
    return out_path


def getWeatherData():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    weather_dir = os.path.join(data_dir, "weatherData")
    wave_dir = os.path.join(data_dir, "waveData")
    wavepngs_dir = os.path.join(data_dir, "wavepngs")

    for d in (data_dir, weather_dir, wave_dir, wavepngs_dir):
        os.makedirs(d, exist_ok=True)

    wave_grib = os.path.join(wave_dir, f"wave_{DATE_STRING}.grib2")
    wave_png = os.path.join(wavepngs_dir, f"wave_{DATE_STRING}.png")
    if not os.path.exists(wave_grib) or not os.path.exists(wave_png):
        convertGribToPng(saveData(downloadWaveData(), "wave", wave_dir))
    else:
        print(f"Wave data already exists for {DATE_STRING}")

    getWeatherForecast(weather_dir)

def cropWeather (globalWeather,bbox):
    croppedWeather = globalWeather.sel(
    latitude=slice(bbox["toplat"], bbox["bottomlat"]),
    longitude=slice(bbox["leftlon"], bbox["rightlon"])
)
    return croppedWeather




if __name__ == "__main__":
    getWeatherData()
