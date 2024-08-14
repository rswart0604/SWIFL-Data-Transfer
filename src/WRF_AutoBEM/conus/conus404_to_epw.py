import xarray as xr
import os
import wrf
import dask
from netCDF4 import Dataset

if __name__ == '__main__':

    CONUS_DIR = "/scratch/rswart/conus404"
    EPW_DIR = "/scratch/rswart/conus404_epws"
    SHP_DIR = "/scratch/rswart/conus404_shapefiles"

    files = [f"{CONUS_DIR}/wrf2d_d01_2020-05-{str(day).zfill(2)}_{str(hour).zfill(2)}:00:00.nc" for day in range(15,32) for hour in range(0,24)]

    wrfin_fps = []

    for file in files:
        wrfin_fps.append(Dataset(file))

    wrf.omp_set_num_threads(4)
    #times = wrf.extract_times(wrfin, timeidx=wrf.ALL_TIMES)
    times = wrf.
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



    for fp in wrfin_fps:
        

    #ds = xr.open_mfdataset(files, parallel=True, chunks='auto')


