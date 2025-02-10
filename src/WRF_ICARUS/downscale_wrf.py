'''
use this script to downscale wrf data to desired resolution
this is done by halving the resolution each time
'''
import time

import xarray as xr
import wrf
import netCDF4
import numpy as np

import defs

import multiprocessing

if __name__ == '__main__':

    tictic = time.time()
    # open my dataset
    fp = 't2_500.nc'
    wrf_nc = netCDF4.Dataset(fp)
    ds = xr.open_dataset(fp)

    # get the projection, lat/lon information, and then change lat/lon to x/y
    params = wrf.get_proj_params(wrf_nc)
    dx = params['DX']
    dist = dx / 4
    wrf_proj = wrf.LambertConformal(**params)
    proj = wrf_proj.cartopy()
    lat, lon = ds.variables['XLAT'].values[0,:,:], ds.variables['XLONG'].values[0,:,:]
    xy_points = proj.transform_points('epsg:4326', lon, lat)[:,:,:2]

    # get dims and t2 (var i want to change)
    dims = lat.shape
    old_t2 = ds.variables['T2'].values[0,:,:]

    # add some variability and return 4 points

    # go thru t2 matrix, do the downscale on each point, then reshape
    old_t2_flattened = old_t2.flatten()
    tic = time.time()
    with multiprocessing.Pool(processes=4) as pool:
        matrices = pool.map(defs.split_point, old_t2_flattened)
    # matrices = np.array([split_point(x).reshape(2,2) for x in ])
    matrices = np.array(matrices)
    print(f'matrices after {time.time()-tic}')
    n_blocks_row = dims[0]
    n_blocks_col = dims[1]
    reshaped = matrices.reshape(n_blocks_row, n_blocks_col, 2, 2)
    new_t2 = np.block([[reshaped[i, j] for j in range(n_blocks_col)] for i in range(n_blocks_row)]).reshape(1,dims[0]*2,dims[1]*2)



    # do lon transformation
    xy_points_flattened = xy_points.reshape(dims[0]*dims[1],2)
    tic = time.time()
    import functools
    split_loc_partial = functools.partial(defs.split_loc, dist=dist, proj=proj, is_lon=True)
    with multiprocessing.Pool(processes=4) as pool:
        lon_matrices = pool.map(split_loc_partial, xy_points_flattened)
    # lon_matrices = np.array([defs.split_loc(x,dist,proj,True).reshape(2,2) for x in ])
    lon_matrices = np.array(lon_matrices)
    reshaped = matrices.reshape(n_blocks_row, n_blocks_col, 2, 2)
    new_lons = np.block([[reshaped[i, j] for j in range(n_blocks_col)] for i in range(n_blocks_row)]).reshape(1,dims[0]*2,dims[1]*2)
    print(f'lons after {time.time()-tic}')


    # do lat transformation
    defs.is_lon = False
    tic = time.time()
    split_loc_partial = functools.partial(defs.split_loc, dist=dist, proj=proj, is_lon=False)
    with multiprocessing.Pool(processes=4) as pool:
        lat_matrices = pool.map(split_loc_partial, xy_points_flattened)
    # lat_matrices = np.array([split_loc(x,dist,proj,False).reshape(2,2) for x in xy_points.reshape(dims[0]*dims[1],2)])
    lat_matrices = np.array(lat_matrices)
    reshaped = matrices.reshape(n_blocks_row, n_blocks_col, 2, 2)
    new_lats = np.block([[reshaped[i, j] for j in range(n_blocks_col)] for i in range(n_blocks_row)]).reshape(1,dims[0]*2,dims[1]*2)
    print(f'lats after {time.time()-tic}')

    # assemble new dataset
    new_attrs = ds.attrs
    new_attrs['history'] = new_attrs['history'] + f";  downscaled from {int(dx)}m to {int(2*dist)}m"
    new_attrs['DX'] = dist*2
    new_attrs['DY'] = dist*2
    new_ds = xr.Dataset(
        data_vars=dict(
            T2=(['Time','south_north','west_east'],new_t2)
        ),
        coords=dict(
            XLAT=(['Time','south_north','west_east'],new_lats),
            XLONG=(['Time','south_north','west_east'],new_lons),
            XTIME=('Time',ds['XTIME'].values),
        ),
        attrs=new_attrs
    )

    new_ds.to_netcdf(f't2_{int(2*dist)}.nc')
    print(f'total time is {time.time()-tictic}')