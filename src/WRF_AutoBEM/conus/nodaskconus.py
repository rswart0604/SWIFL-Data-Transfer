import numpy as np
import xarray as xr
import wrf
import pandas as pd
import geopandas as gpd
import os
import time



if __name__ == '__main__':


    import os, psutil;
    proc = psutil.Process(os.getpid())

    def get_mem():
        print(f'mem is {proc.memory_info().rss}')
    print('hi')
    epwdir = '/scratch/rswart/conus_epws'
    WRF_FILES_DIR = '/scratch/rswart/conus404'
    FILES = [os.path.join(WRF_FILES_DIR, x) for x in os.listdir(WRF_FILES_DIR)]
    print('about to read files')
    old = time.time()
    raw_ds = xr.open_mfdataset(FILES[:30], parallel=True, chunks={}) 
    print(f'reading time was {time.time()-old}')

    LAT_MIN, LAT_MAX = 31.4, 36.654
    LON_MAX, LON_MIN = -108.9, -114.657
    mask = (raw_ds['XLAT'] > LAT_MIN) & (raw_ds['XLAT'] < LAT_MAX) & (raw_ds['XLONG'] > LON_MIN) & (raw_ds['XLONG'] < LON_MAX)
    print(mask)
    ds = raw_ds.where(mask.compute(), drop=True)
 
    lat = ds['XLAT']
    lon = ds['XLONG']
    real_lon = ds['XLONG'].values.ravel()[((ds['XLAT'] > LAT_MIN) & (ds['XLAT'] < LAT_MAX) & (ds['XLONG'] > LON_MIN) & (ds['XLONG'] < LON_MAX)).values.ravel()]
    real_lat = ds['XLAT'].values.ravel()[((ds['XLAT'] > LAT_MIN) & (ds['XLAT'] < LAT_MAX) & (ds['XLONG'] > LON_MIN) & (ds['XLONG'] < LON_MAX)).values.ravel()]
    get_mem()

    import pandas as pd
    df = pd.DataFrame(ds['Time'])
    df[0] = df[0].dt.tz_localize("UTC")
    df[0] = df[0].dt.tz_convert("America/Phoenix")
    times = df[0].to_numpy()

    get_mem()

    from wrf.extension import _uvmet, _rh
    from wrf.g_wind import _calc_wspd_wdir
    
    
    ## some stuff to calculate cone for lambert conformal
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
    ##


    wrf.omp_set_num_threads(3)
    
    result_shape = ds['TD2'].shape
    wspd, wdir = np.empty(result_shape, np.float32), np.empty(result_shape, np.float32)
    print('a')
    get_mem()
    dewpoint = ds['TD2']
    print('b')
    get_mem()
    rh = np.empty(result_shape, np.float32)
    pres = ds['PSFC']
    print('c')
    get_mem()
    swnorm = ds['SWNORM']
    
    t2 = ds['T2']
    glw = ds['GLW']
    cldfra = np.zeros(result_shape, np.float32)
    hgt = ds['Z'][0,:,:].values

    print('d')
    get_mem()

    import time
    for t in range(len(FILES)):
        old = time.time()

        u, v = _uvmet(ds['U10'][t], ds['V10'][t], lat, lon, cen_lon, cone)
        u = np.expand_dims(u, axis=0)
        v = np.expand_dims(v, axis=0)
        wspd[t], wdir[t] = _calc_wspd_wdir(u,v,False,'m s-1')
        
        _psfc = pres[t]
        _q2 = ds['Q2'][t]
        _t2 = t2[t]
        rh[t] = _rh(_q2, _psfc, _t2)
        
        # todo, cldfra
        get_mem()
        print(f'time in loop: {time.time()-old}')

    import os

    def make_epw(num, i, j):
        old = time.time()

        data_dict = {
                "!Year": [x.year for x in times],
                "Month": [x.month for x in times],
                "Day": [x.day for x in times], 
                "Hour": [x.hour+1 for x in times],
                "Minute": [x.minute for x in times],
                "Weather station code": ["?9?9?9?9E0?9?9?9?9?9?9?9?9?9?9?9?9?9?9?9*9*9?9?9?9" for x in times],
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
                "Wind Direction {deg}": wdir[:,i,j],
                "Wind Speed {m/s}": wspd[:,i,j],
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
        print(time.time()-old)

        df = pd.DataFrame(data_dict)
        print(time.time()-old)
        
        f = open(os.path.join(epwdir, f'{num}.header'), 'w')
        f.write(f'LOCATION,Phoenix-Sky Harbor Intl AP,AZ,USA,TMY3,722780,{round(lat[i][j].values.item(),5)},{round(lon[i][j].values.item(),5)},-7.0,{round(hgt[i][j],1)}\n')
        # todo, add ground temp
        f.close()
        print(time.time()-old)

        df.to_csv(os.path.join(epwdir, f'{num}.epw'), header=False, index=False)
        print(time.time()-old)
        
        print('======')

        del df



    a = ((ds['XLAT'] > LAT_MIN) & (ds['XLAT'] < LAT_MAX) & (ds['XLONG'] > LON_MIN) & (ds['XLONG'] < LON_MAX))
    indices = np.nonzero(a.values)

    old = time.time()
    for num in range(len(times)):
        make_epw(num, indices[0][num], indices[1][num])           
    print(f'total time is {time.time()-old}')



