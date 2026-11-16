import os
import math
import numpy as np
import xarray as xr

RES = 0.25  # grid spacing of the weather file and the sea mask (degrees)


def cropToBox(ds, bbox):
    lon0 = round(float(ds.longitude[0]) / RES) * RES
    n = ds.sizes["longitude"]
    cols = np.arange(math.ceil((bbox["leftlon"] - lon0) / RES),
                     math.floor((bbox["rightlon"] - lon0) / RES) + 1)
    if round(n * RES) == 360:
        idx = cols % n                                 
    else:
        cols = cols[(cols >= 0) & (cols < n)]
        idx = cols
    return (ds.sel(latitude=slice(bbox["toplat"], bbox["bottomlat"]))  
              .isel(longitude=idx)
              .assign_coords(longitude=lon0 + cols * RES))

class GeographicDataService:
    def __init__(self):
        self.seaMask = None

    def getSeaMask(self, bbox):
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        geographic_dir = os.path.join(data_dir, "geographicData")
        sea_mask_file = os.path.join(geographic_dir, "sea_mask_0.25deg.nc")
        
        if os.path.exists(sea_mask_file):
            globalSeaMask = xr.open_dataarray(sea_mask_file)
            self.cropSeaMask(globalSeaMask, bbox)
        else:
            raise FileNotFoundError(f"Sea mask file not found at {sea_mask_file}")

    def cropSeaMask(self, globalSeaMask, bbox):
        croppedSeaMask = cropToBox(globalSeaMask, bbox)

        self.seaMask = croppedSeaMask
        return self.seaMask
    
    
