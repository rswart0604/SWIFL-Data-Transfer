"""
the purpose of this script is to take wrf output and turn it into
    daymet format. same variable types, etc. not the same resolution, etc
    this will create multiple nc files
"""
import xarray as xr
import wrf
import pandas as pd
from netCDF4 import Dataset
import numpy as np

WRF_FP = '/scratch/rswart/wrfout_d03_2020-05-16_00_1km_ctrl.nc'

def get_day_length(dayOfYear, lat):
    latInRad = np.deg2rad(lat)
    declinationOfEarth = 23.45 * np.sin(np.deg2rad(360.0 * (283.0 + dayOfYear) / 365.0))
    if -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) <= -1.0:
        return 24*60
    elif -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) >= 1.0:
        return 0
    else:
        hourAngle = np.rad2deg(np.arccos(-np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth))))
        return int((2.0 * hourAngle / 15.0) * 60)


# open up our wrf output
ds = xr.open_dataset(WRF_FP)
wrfin = Dataset(WRF_FP)


# get time variables
# first have to change time zones
old_times = wrf.extract_times(wrfin, timeidx=wrf.ALL_TIMES)
_ = pd.DataFrame(old_times)  # some bs to fix time zone
_[0] = _[0].dt.tz_localize("UTC")
_[0] = _[0].dt.tz_convert("America/Phoenix")
times = _[0].to_numpy()
hours = [x.hour for x in times]
# then we need to round to the nearest full day
first_index = hours.index(0)
last_index = len(hours) - hours[::-1].index(0) - 1
times = times[first_index:last_index]
old_date = pd.Timestamp(year=1950, month=1, day=1, tz="America/Phoenix")
# days since 1950 jan 1 00:00:00
days_since = [(x-old_date).days for x in times]
time_var_tmp = list(set(days_since[first_index:last_index]))
time_var = [x + 0.5 for x in time_var_tmp]  # weird thing with like "middle of day"

time_bnds_var = [[x, x+1] for x in time_var_tmp]

first_doy = pd.Timestamp(year=2019, month=12, day=31, tz='America/Phoenix')
yearday = [(x-first_doy).days for x in times]
yearday_var = list(set(yearday[first_index:last_index]))


lat = ds['XLAT'][0,:,:]
lon = ds['XLONG'][0,:,:]


# the magic x and y numbers are from the actual eastings/northings values stuff
#   from the lambert conformal projection that the wrf output uses.
#   if the wrf projection changes, they should also change
from pyproj import Proj
# this string is from the wrf ncdump output
proj_string = """
+proj=lcc
+lat_1=33
+lat_2=33
+lat_0=33.62058
+lon_0=-111.5
+x_0=0
+y_0=0
+a=6378137
+rf=298.257223563
"""

proj = Proj(proj_string)
easting_start, northing_start = proj(ds['XLONG'][0,0,0], ds['XLAT'][0,0,0])

x_var = [easting_start + 1000*x for x in range(len(ds.west_east))]
y_var = [northing_start + 1000*x for x in range(len(ds.south_north))]


# make a bunch of raw variables and then transform them to fit the 1day format
prcp_raw = ds['RAINNC'][first_index:last_index,:,:]
temp_raw = ds['T2'][first_index:last_index,:,:]
srad_raw = ds['SWDOWN'][first_index:last_index,:,:]
swe_raw = ds['SWE'][first_index:last_index,:,:]

# transform data (ie prcp should be summed)
prcp_var = np.zeros((len(yearday_var),prcp_raw.shape[1],prcp_raw.shape[2]))
tmin_var = np.zeros((len(yearday_var),temp_raw.shape[1],temp_raw.shape[2]))
tmax_var = np.zeros((len(yearday_var),temp_raw.shape[1],temp_raw.shape[2]))
srad_var = np.zeros((len(yearday_var),srad_raw.shape[1],srad_raw.shape[2]))
swe_var = np.zeros((len(yearday_var),swe_raw.shape[1],swe_raw.shape[2]))
vp_var = np.zeros((len(yearday_var),swe_raw.shape[1],swe_raw.shape[2]))

vectorized_get_day_length = np.vectorize(get_day_length)
doy_col = np.array(yearday)[:, np.newaxis, np.newaxis]  # todo idk about this
dayl_var = vectorized_get_day_length(doy_col, lat)

for t in range(len(yearday_var)):
    prcp_var[t,:,:] = np.sum(prcp_raw[t*24:t*24 + 24,:,:], axis=0)
    tmin_var[t,:,:] = np.min(temp_raw[t*24:t*24 + 24,:,:], axis=0)
    tmax_var[t,:,:] = np.max(temp_raw[t*24:t*24 + 24,:,:], axis=0)
    srad_var[t,:,:] = np.average(srad_raw[t*24:t*24 + 24][srad_raw[t*24:t*24 + 24] > 0.0])
    swe_var[t,:,:] = np.mean(swe_raw[t*24:t*24 + 24,:,:], axis=0)

for t in range(first_index, last_index):
    dewpoint = wrf.getvar(wrfin, 'td2', timeidx=t, units='K')
    vp_var[t] = 6.11 * np.exp(5321 * (1/273 - 1/dewpoint))


# make attributes for everything
x_attr = dict(units='m', long_name='x coordinate of projection', standard_name = "projection_x_coordinate")
y_attr = dict(units='m', long_name='y coordinate of projection', standard_name = "projection_y_coordinate")
lat_attr = dict(units = "degrees_east", long_name = "latitude coordinate", standard_name = "latitude")
lon_attr = dict(units = "degrees_east", long_name = "longitude coordinate", standard_name = "longitude")
time_attr = dict(standard_name = "time", calendar = "standard", units = "days since 1950-01-01 00:00:00", 
    bounds = "time_bnds", long_name = "24-hour day based on local time")
yearday_attr = dict(long_name = "day of year (DOY) starting with day 1 on January 1st")
# all of the actual variables
prcp_attr = dict(_FillValue = -9999.0, long_name = "daily total precipitation", units = "mm/day",
    missing_value = -9999.0, coordinates = "lat lon", grid_mapping = "lambert_conformal_conic", cell_methods = "area: mean time: sum")
dayl_attr = dict(_FillValue = -9999.0, long_name = "daylength", units = "s",
    missing_value = -9999.0, coordinates = "lat lon", grid_mapping = "lambert_conformal_conic", cell_methods = "area: mean")
swe_attr = dict(_FillValue = -9999.0, long_name = "snow water equivalent", units = "kg/m2",
    missing_value = -9999.0, coordinates = "lat lon", grid_mapping = "lambert_conformal_conic", cell_methods = "area: mean time: mean")
swrad_attr = dict(_FillValue = -9999.0, long_name = "daylight average incident shortwave radiation", units = "W/m2",
    missing_value = -9999.0, coordinates = "lat lon", grid_mapping = "lambert_conformal_conic", cell_methods = "area: mean time: mean")
tmin_attr = dict(_FillValue = -9999.0, long_name = "daily minimum temperature", units = "degrees C",
    missing_value = -9999.0, coordinates = "lat lon", grid_mapping = "lambert_conformal_conic", cell_methods = "area: mean time: minimum")
tmax_attr = dict(_FillValue = -9999.0, long_name = "daily maximum temperature", units = "degrees C",
    missing_value = -9999.0, coordinates = "lat lon", grid_mapping = "lambert_conformal_conic", cell_methods = "area: mean time: maximum")
vp_attr = dict(_FillValue = -9999.0, long_name = "daily average vapor pressure", units = "Pa",
    missing_value = -9999.0, coordinates = "lat lon", grid_mapping = "lambert_conformal_conic", cell_methods = "area: mean time: mean")



new_ds = xr.Dataset(
    data_vars=dict(
        yearday=(['time'], yearday_var, yearday_attr),
        time_bnds=(['time','nv'], time_bnds_var),
        prcp=(['time','y','x'], prcp_var, prcp_attr)
    ),
    coords=dict(
        x=('x', x_var, x_attr),
        y=('y',y_var, y_attr),
        lat=(('y','x'), lat.data, lat_attr),
        lon=(('y','x'), lon.data, lon_attr),
        time=('time',time_var, time_attr)
    ),
    attrs=dict(
        start_year = 2020,
        source='WRF',
        Conventions = "CF-1.6",
    )
)
new_ds.to_netcdf('/scratch/rswart/test.nc')
new_ds.drop_vars('prcp')
new_ds['dayl']

