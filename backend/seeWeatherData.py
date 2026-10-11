import os
import xarray as xr
import matplotlib.pyplot as plt


def seeWeatherData():
    data_dir = os.path.join(os.path.dirname(__file__), "data/weatherData")
    nc_path = os.path.join(data_dir, "weather_20261011_7day.nc")

    if os.path.exists(nc_path):
        ds = xr.open_dataset(nc_path)
        for step in range(len(ds.step)):
            step_ds=ds.isel(step=step)
            print(step_ds['valid_time'].values)
            
        # Plot first forecast step for each variable
        # step0 = ds.isel(step=0)
        # for var_name, data in step0.data_vars.items():
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     mesh = ax.pcolormesh(
        #         data.longitude, data.latitude, data.values, cmap="turbo", shading="auto"
        #     )
        #     fig.colorbar(
        #         mesh,
        #         ax=ax,
        #         label=f"{data.attrs.get('long_name', var_name)} ({data.attrs.get('units', '')})",
        #     )
        #     ax.set_title(f"{var_name} - step 0 - 20260918")
        #     out = os.path.join(data_dir, f"weather_{var_name}_20260918.png")
        #     fig.savefig(out, dpi=150, bbox_inches="tight")
        #     plt.close(fig)
        #     print(f"saved {out}")
        # ds.close()
        return


if __name__ == "__main__":
    seeWeatherData()
