import numpy as np
import math
from shapely.geometry import Polygon
from netCDF4 import Dataset
import xarray as xr
import pandas as pd
import os
import wrf
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
    WRF_FP = '/scratch/rswart/wrfout_d03_2020-05-16_00_1km_ctrl.nc'
    OUT_DIR = '/scratch/rswart'
    ###
    
    old = time.time()

    epwdir = os.path.join(OUT_DIR, 'epws')
    if not os.path.exists(epwdir):
        os.mkdir(os.path.join(OUT_DIR,'epws'))
    
    import gc

    wrf.omp_set_num_threads(4)
    ds = xr.open_dataset(WRF_FP)
    wrfin = Dataset(WRF_FP)
    times = wrf.extract_times(wrfin, timeidx=wrf.ALL_TIMES)
    result_shape = (len(times), 414, 354)  # todo change this
    _10wspd, _10wdir = np.empty(result_shape, np.float32), np.empty(result_shape, np.float32)
    dewpoint = np.empty(result_shape, np.float32)
    rh = np.empty(result_shape, np.float32)
    pres = np.empty(result_shape, np.float32)
    swnorm = np.empty(result_shape, np.float32)
    t2 = np.empty(result_shape, np.float32)
    glw = np.empty(result_shape, np.float32)
    cldfra = np.empty(result_shape, np.float32)
    lat = ds['XLAT'][0,:,:].values
    lon = ds['XLONG'][0,:,:].values
    hgt = ds['HGT'][0,:,:].values
    for t in range(len(times)):
        _10wspd[t,:,:], _10wdir[t,:,:] = wrf.getvar(wrfin, "uvmet10_wspd_wdir", timeidx=t)
        dewpoint[t,:,:] = wrf.getvar(wrfin, 'td2', timeidx=t, units='degC')
        rh[t,:,:] = wrf.getvar(wrfin, 'rh2', timeidx=t)
        swnorm[t,:,:] = wrf.getvar(wrfin, 'SWDOWN', timeidx=t) / wrf.getvar(wrfin, 'COSZEN', timeidx=t)
        t2[t,:,:] = wrf.getvar(wrfin, 'T2', timeidx=t) - 273
        pres[t,:,:] = wrf.getvar(wrfin, 'PSFC', timeidx=t) * 0.01  # Pa, not hPa
        glw[t,:,:] = wrf.getvar(wrfin, 'GLW', timeidx=t)
        cldfra[t,:,:] = np.max(ds['CLDFRA'][t,:,:,:], axis=0).values

    # modify times to fit our local needs (convert from utc to az time)
    df = pd.DataFrame(times)
    df[0] = df[0].dt.tz_localize("UTC")
    df[0] = df[0].dt.tz_convert("America/Phoenix")
    new_times = df[0].to_numpy()

    west_east = ds.sizes['west_east']
    south_north = ds.sizes['south_north']


#    tmy_df = pd.read_csv('/home/rswart/tmy.epw')
#    tmy_index = tmy_df.loc[(tmy_df['Month'] == new_times[0].month) & (tmy_df['Day'] == new_times[0].day) \
#            & (tmy_df['Hour'] == new_times[0].hour+1)].index.to_list()[0]

    print(time.time()-old)
    print("////////")

    def make_epw(num):
        #old = time.time()

        i = num // west_east
        j = num % west_east
        data_dict = {
                "!Year": [x.year for x in new_times],
                "Month": [x.month for x in new_times],
                "Day": [x.day for x in new_times], 
                "Hour": [x.hour+1 for x in new_times],
                "Minute": [x.minute for x in new_times],
                "Weather station code": ["?9?9?9?9E0?9?9?9?9?9?9?9?9?9?9?9?9?9?9?9*9*9?9?9?9" for x in new_times],
                "Dry bulb temperature {C}": t2[:,i,j],
                "Dew point temperature {C}": dewpoint[:,i,j],
                "Relative Humidity {%}": rh[:,i,j],
                "Atmospheric Pressure {Pa}": pres[:,i,j],
                "Extraterrestrial Horizontal Radiation {Wh/m2}": 9999*np.ones(len(times), dtype=np.int32),
                "Extraterrestrial Direct Normal Radiation {Wh/m2}": 9999*np.ones(len(times), dtype=np.int32),
                "Horizontal Infrared Radiation Intensity from Sky {Wh/m2}": glw[:,i,j],
                "Global Horizontal Radiation {Wh/m2}": 9999*np.ones(len(times), dtype=np.int32),
                "Direct Normal Radiation {Wh/m2}": 0.8*swnorm[:,i,j],
                "Diffuse Horizontal Radiation {Wh/m2}": 0.2*swnorm[:,i,j],
                "Global Horizontal Illuminance {lux}": 999999*np.ones(len(times), dtype=np.int32),
                "Direct Normal Illuminance {lux}": 999999*np.ones(len(times), dtype=np.int32),
                "Diffuse Horizontal Illuminance {lux}": 999999*np.ones(len(times), dtype=np.int32),
                "Zenith Luminance {Cd/m2}": 999999*np.ones(len(times), dtype=np.int32),
                "Wind Direction {deg}": _10wdir[:,i,j],
                "Wind Speed {m/s}": _10wspd[:,i,j],
                "Total Sky Cover {.1}": cldfra[:,i,j] * 10.0,
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
        f.write(f'LOCATION,Phoenix-Sky Harbor Intl AP,AZ,USA,TMY3,722780,{round(lat[i][j],5)},{round(lon[i][j],5)},-7.0,{round(hgt[i][j],1)}\n')
        f.close()
        #print(time.time()-old)

        df.to_csv(os.path.join(epwdir, f'{num}.epw'), header=False, index=False)
        #print(time.time()-old)
        
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

