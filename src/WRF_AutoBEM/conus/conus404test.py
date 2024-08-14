import numpy as np
import math
from shapely.geometry import Polygon
from netCDF4 import Dataset
import xarray as xr
import pandas as pd
import os
import wrf
from wrf.extension import _uvmet, _rh
from wrf.g_wind import _calc_wspd_wdir
import time
import geopandas as gpd
from geopy.distance import distance
"""
this script takes in a wrfout file (WRF_FP), goes through it, and creates a time series
    of several variables (relevant to EnergyPlus) for each wrf grid cell, giving it a unique id
    in an epw file
    this id also refers to a unique shapefile that has the geometry of the grid cell
    all epws are stores in a dir called "epws", all shapefile folders in a dir called "shapefiles"
    enabled with openmp. run with 4 cores for decent speeds
"""
if __name__ == '__main__':
    
    ### change upon each use
    WRF_FP = '/scratch/rswart/conus404.nc'
    OUT_DIR = '/scratch/rswart'
    ###
    
    old = time.time()

    epwdir = os.path.join(OUT_DIR, 'conus404_epws')
    if not os.path.exists(epwdir):
        os.mkdir(os.path.join(OUT_DIR,'conus404_epws'))
    
    import gc

    def get_ravels(data_array, mask):
        vals = data_array.values if type(data_array) is not np.ndarray else data_array
        tmp_arr = vals.reshape(vals.shape[0], -1)
        return np.array([tmp_arr[i, mask] for i in range(tmp_arr.shape[0])])

    ds = xr.open_dataset(WRF_FP)
    times = ds['Time']
    LAT_MIN, LAT_MAX = 31.4, 36.654
    LON_MAX, LON_MIN = -108.9, -114.657
    mask = ((ds['XLAT'] > LAT_MIN) & (ds['XLAT'] < LAT_MAX) & (ds['XLONG'] > LON_MIN) & (ds['XLONG'] < LON_MAX)).values.ravel()
    flat_lats = ds['XLAT'].values.ravel()[mask]
    flat_lons = ds['XLONG'].values.ravel()[mask]
    swnorm = get_ravels(ds['SWNORM'], mask)
    glw = get_ravels(ds['GLW'], mask)
    hgt = get_ravels(ds['Z'], mask)[0]
    dewpoint = get_ravels(ds['TD2'], mask)

    u10 = ds['U10']
    v10 = ds['V10']
    pres = ds['PSFC']
    t2 = ds['T2']
    q2 = ds['Q2']

    from math import fabs, log, tan, sin, cos, pi
    true_lat1 = ds.attrs['TRUELAT1']
    true_lat2 = ds.attrs['TRUELAT2']
    cen_lon = ds.attrs['CEN_LON']

    radians_per_degree = pi/180.0
    if((fabs(true_lat1 - true_lat2) > 0.1) and
                        (fabs(true_lat2 - 90.) > 0.1)):
        cone = (log(cos(true_lat1*radians_per_degree)) -
                log(cos(true_lat2*radians_per_degree)))
        cone = (cone /
                (log(tan((45.-fabs(true_lat1/2.))*radians_per_degree))
                 - log(tan((45.-fabs(true_lat2/2.)) *
                           radians_per_degree))))
    else:
        cone = sin(fabs(true_lat1)*radians_per_degree)

    wrf.omp_set_num_threads(2)
    result_shape = (len(times), ds['XLAT'].shape[0], ds['XLAT'].shape[1])
    _10wspd, _10wdir = np.empty(result_shape, np.float32), np.empty(result_shape, np.float32)
    rh = np.empty(result_shape, np.float32)
    lat = ds['XLAT'].values
    lon = ds['XLONG'].values
    for t in range(len(times)):
        u, v = _uvmet(u10[t], v10[t], lat, lon, cen_lon, cone)
        u = np.expand_dims(u, axis=0)
        v = np.expand_dims(v, axis=0)
        _10wspd[t], _10wdir[t] = _calc_wspd_wdir(u,v,False,'m s-1')
        rh[t] = _rh(q2[t], pres[t], t2[t]) 
        #cldfra[t,:,:] = np.max(ds['CLDFRA'][t,:,:,:], axis=0).values

    _10wspd = get_ravels(_10wspd, mask)
    _10wdir = get_ravels(_10wdir, mask)
    rh = get_ravels(rh, mask)
    pres = get_ravels(pres, mask)
    t2 = get_ravels(t2, mask)

    # modify times to fit our local needs (convert from utc to az time)
    df = pd.DataFrame(times)
    df[0] = df[0].dt.tz_localize("UTC")
    df[0] = df[0].dt.tz_convert("America/Phoenix")
    new_times = df[0].to_numpy()
    print(new_times)

    west_east = ds.sizes['west_east']
    south_north = ds.sizes['south_north']

    lat = flat_lats
    lon = flat_lons

#    tmy_df = pd.read_csv('/home/rswart/tmy.epw')
#    tmy_index = tmy_df.loc[(tmy_df['Month'] == new_times[0].month) & (tmy_df['Day'] == new_times[0].day) \
#            & (tmy_df['Hour'] == new_times[0].hour+1)].index.to_list()[0]

    print(time.time()-old)
    print("////////")

    def make_epw(num):
        old = time.time()

        data_dict = {
                "!Year": [x.year for x in new_times],
                "Month": [x.month for x in new_times],
                "Day": [x.day for x in new_times], 
                "Hour": [x.hour+1 for x in new_times],
                "Minute": [x.minute for x in new_times],
                "Weather station code": ["?9?9?9?9E0?9?9?9?9?9?9?9?9?9?9?9?9?9?9?9*9*9?9?9?9" for x in new_times],
                "Dry bulb temperature {C}": t2[:,num],
                "Dew point temperature {C}": dewpoint[:,num],
                "Relative Humidity {%}": rh[:,num],
                "Atmospheric Pressure {Pa}": pres[:,num],
                "Extraterrestrial Horizontal Radiation {Wh/m2}": 9999*np.ones(len(times), dtype=np.int32),
                "Extraterrestrial Direct Normal Radiation {Wh/m2}": 9999*np.ones(len(times), dtype=np.int32),
                "Horizontal Infrared Radiation Intensity from Sky {Wh/m2}": glw[:,num],
                "Global Horizontal Radiation {Wh/m2}": 9999*np.ones(len(times), dtype=np.int32),
                "Direct Normal Radiation {Wh/m2}": 0.8*swnorm[:,num],
                "Diffuse Horizontal Radiation {Wh/m2}": 0.2*swnorm[:,num],
                "Global Horizontal Illuminance {lux}": 999999*np.ones(len(times), dtype=np.int32),
                "Direct Normal Illuminance {lux}": 999999*np.ones(len(times), dtype=np.int32),
                "Diffuse Horizontal Illuminance {lux}": 999999*np.ones(len(times), dtype=np.int32),
                "Zenith Luminance {Cd/m2}": 999999*np.ones(len(times), dtype=np.int32),
                "Wind Direction {deg}": _10wdir[:,num],
                "Wind Speed {m/s}": _10wspd[:,num],
                "Total Sky Cover {.1}": np.zeros(len(times)),
                "Opaque Sky Cover {.1}": 99*np.ones(len(times), dtype=np.int32),
                "Visibility {km}": 9999*np.ones(len(times), dtype=np.float32),
                "Ceiling Height {m}": 9999*np.ones(len(times), dtype=np.int32),
                "Present Weather Observation": 9*np.ones(len(times), dtype=np.int32), 
                "Present Weather Codes": 999999*np.ones(len(times), dtype=np.int32),
                "Precipitable Water {mm}": 999*np.ones(len(times), dtype=np.int32),
                "Aerosol Optical Depth {.001}": 999*np.ones(len(times)),
                "Snow Depth {cm}": 999*np.ones(len(times), dtype=np.int32),
                "Days Since Last Snow": 99*np.ones(len(times), dtype=np.int32),
                "Albedo {.01}": np.zeros(len(times)),
                "Liquid Precipitation Depth {mm}": np.zeros(len(times)),
                "Liquid Precipitation Quantity {hr}": np.zeros(len(times))
            }
        #print(time.time()-old)

        df = pd.DataFrame(data_dict)
        #print(time.time()-old)
        
        f = open(os.path.join(epwdir, f'{num}.header'), 'w')
        f.write(f'LOCATION,Phoenix-Sky Harbor Intl AP,AZ,USA,TMY3,722780,{round(lat[num],5)},{round(lon[num],5)},-7.0,{round(hgt[num],1)}\n')
        f.close()
        #print(time.time()-old)

        df.to_csv(os.path.join(epwdir, f'{num}.epw'), header=False, index=False)
        print(time.time()-old)
        
        #print('======')

        del df
        gc.collect()
    
    old = time.time()
    for i in range(lat.size):
        make_epw(i)
    print(time.time()-old)
    #import multiprocessing
    #with multiprocessing.Pool(2) as p:
    #    p.map(make_epw, range(500))

