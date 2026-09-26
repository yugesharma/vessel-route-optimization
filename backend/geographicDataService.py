import os
import xarray as xr

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
        croppedSeaMask = globalSeaMask.sel(
            latitude=slice(bbox["toplat"], bbox["bottomlat"]),
            longitude=slice(bbox["leftlon"], bbox["rightlon"])
        )

        self.seaMask = croppedSeaMask
        return self.seaMask
    

