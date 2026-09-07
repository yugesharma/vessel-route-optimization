import os
import glob
import requests
from datetime import date
import xarray as xr
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATE_STRING = date.today().strftime("%Y%m%d")

def downloadWaveData():
    baseUrl = (
        "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_wave_0p25.pl"
        f"?dir=%2Fgefs.{DATE_STRING}%2F00%2Fwave%2Fgridded"
        "&file=gefs.wave.t00z.c00.global.0p25.f000.grib2"
        "&var_HTSGW=on"
        "&lev_surface=on"
    )

    response = requests.get(baseUrl, timeout=120)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to download wave data: HTTP {response.status_code}"
        )

    print("Wave data downloaded successfully")
    return response


def saveWaveData(response):
    out_path = os.path.join(os.path.join(os.path.dirname(__file__), "data"), f"wave_{DATE_STRING}.grib2")
    with open(out_path, "wb") as f:
        f.write(response.content)
    print(f"Wave data saved to {out_path}")
    return out_path


def convertGribToPng(gribFile):
    for stale in glob.glob(f"{gribFile}.*.idx"):
        os.remove(stale)
    ds = xr.open_dataset(gribFile, engine="cfgrib")
    
    print('--------------A look at the data------------------')
    print('keys:', ds.keys())
    print(ds["swh"].sel(latitude=20, longitude=280, method="nearest").item())
    print('max:', ds["swh"].max().item())
    print('min:', ds["swh"].min().item())
    
    data = ds['swh']
    wavepngsDir = os.path.join(os.path.join(os.path.dirname(__file__), "data"), "wavepngs")
    os.makedirs(wavepngsDir, exist_ok=True)
    out_path = os.path.join(wavepngsDir, f"wave_{DATE_STRING}.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    mesh = ax.pcolormesh(
        data.longitude, data.latitude, data.values, cmap="turbo", shading="auto"
    )
    fig.colorbar(mesh, ax=ax, label=f"{data.attrs.get('long_name', 'swh')} ({data.attrs.get('units', 'm')})")
    ax.set_title(f"Significant Wave Height - {DATE_STRING}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Wave map saved to {out_path}")
    ds.close()
    return out_path


def getWaveData():
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "data")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "wavepngs")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "wavepngs"), exist_ok=True)
    gribFile = os.path.join(os.path.join(os.path.dirname(__file__), "data"), f"wave_{DATE_STRING}.grib2")
    if not os.path.exists(gribFile) or not os.path.exists(os.path.join(os.path.dirname(__file__), "wavepngs", f"wave_{DATE_STRING}.png")):
        response = downloadWaveData()
        gribFile = saveWaveData(response)
        convertGribToPng(gribFile)
    else:
        print(f"Wave data already exists for {DATE_STRING}")

if __name__ == "__main__":
    getWaveData()
