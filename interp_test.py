import xarray as xr
import numpy as np
from pyproj import Proj, transform
from scipy.interpolate import griddata

# Load the NetCDF file
data = xr.open_dataset("t2.nc")
T2 = data['T2']  # Temperature at 2 meters
XLONG = data['XLONG']  # Longitude grid
XLAT = data['XLAT']    # Latitude grid

# Define the Lambert Conformal projection for the WRF output
proj_lcc = Proj(proj='lcc', lat_1=data.TRUELAT1, lat_2=data.TRUELAT2,
                lat_0=data.CEN_LAT, lon_0=data.CEN_LON)

# Convert latitude and longitude to Lambert Conformal projected coordinates in meters
x, y = proj_lcc(XLONG.values, XLAT.values)

# Define the new 500m grid in the projected coordinate space
x_min, x_max = x.min(), x.max()
y_min, y_max = y.min(), y.max()

x_new = np.arange(x_min, x_max, 500)  # 500 m spacing
y_new = np.arange(y_min, y_max, 500)  # 500 m spacing
x_new_grid, y_new_grid = np.meshgrid(x_new, y_new)

# Flatten the original arrays for interpolation
points = np.array([x.ravel(), y.ravel()]).T
values = T2.values.ravel()

# Perform the interpolation in the projected coordinate space
T2_new = griddata(points, values, (x_new_grid, y_new_grid), method='linear')

# Convert the interpolated data to an xarray DataArray
T2_new_da = xr.DataArray(
    T2_new,
    dims=["south_north", "east_west"],
    coords={
        "x": (("south_north", "east_west"), x_new_grid),
        "y": (("south_north", "east_west"), y_new_grid),
    },
    name="T2_500m"
)
