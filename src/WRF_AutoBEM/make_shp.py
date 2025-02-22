import numpy as np
import math
from shapely.geometry import Polygon
import geopandas as gpd
from geopy.distance import distance
import xarray as xr
import time
import os
import multiprocessing

'''
This file takes the wrfout that you are using as input and makes the "mesh" for it in the form
    of several shp files. These contain no information other than the bounds of each wrf grid and are numbered
    from 1 to the number of grid cells.
    
The purpose of these shp files is to allow AutoBEM to detect what buildings are in each wrf grid cell
    and then use the corresponding epw file for those buildings
'''

if __name__ == '__main__':


    WRF_FP = '/scratch/rswart/wrfout_d03_2020-05-16_00_1km_ctrl.nc'
    OUT_DIR = '/scratch/rswart'
    DIAG_LENGTH = math.sqrt(2)*.5

    shpdir = os.path.join(OUT_DIR, 'shapefiles')
    ds = xr.open_dataset(WRF_FP)
    lat = ds['XLAT'][0,:,:].values
    lon = ds['XLONG'][0,:,:].values

    west_east = ds.sizes['west_east']
    south_north = ds.sizes['south_north']

    def create_square(lat, lon, diaglength):
        # 0north, 90east, 180south, 270west (or -90west)
        # distance is done in km implicitly
        ur = distance(diaglength).destination((lat, lon), bearing=45)[0:2][::-1]
        ul = distance(diaglength).destination((lat, lon), bearing=-45)[0:2][::-1]
        lr = distance(diaglength).destination((lat, lon), bearing=135)[0:2][::-1]
        ll = distance(diaglength).destination((lat, lon), bearing=225)[0:2][::-1]
        return Polygon([ll, lr, ur, ul])

    def do_thing(num):
        i = num // west_east
        j = num % west_east
        gdf = gpd.GeoDataFrame({'geometry': [create_square(lat[i,j],lon[i,j],DIAG_LENGTH)]})
        tmp_shpdir = os.path.join(shpdir, f'{num}_shapefile')
        if not os.path.exists(tmp_shpdir):
            os.mkdir(tmp_shpdir)
        gdf.to_file(os.path.join(tmp_shpdir, f'{num}.shp'))

    oldold = time.time()
    with multiprocessing.Pool(4) as p:
        p.map(do_thing, range(lat.size))
    print(f'total time is {time.time()-oldold}')

