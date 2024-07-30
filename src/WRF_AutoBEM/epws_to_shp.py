import geopandas as gpd
import pandas as pd
import os
import numpy as np
from dask import delayed, compute
from dask.distributed import Client, LocalCluster


if __name__ == '__main__':

    files = np.loadtxt('/home/rswart/tiles.txt', dtype=int)

    cluster = LocalCluster(n_workers=6, threads_per_worker=1)
    client = Client(cluster)

    names = ['!Year', 'Month', 'Day', 'Hour', 'Minute', 'Dry bulb temperature {C}', 
             'Dew point temperature {C}', 'Relative Humidity {%}', 'Atmospheric Pressure {Pa}',
             'Horizontal Infrared Radiation Intensity from Sky {Wh/m2}', 'Direct Normal Radiation {Wh/m2}',
             'Diffuse Horizontal Radiation {Wh/m2}', 'Wind Direction {deg}', 'Wind Speed {m/s}', 'Total Sky Cover {.1}']

    def get_epw(epw_num: int) -> pd.DataFrame:
        gdf = gpd.read_file(f'/scratch/rswart/shapefiles/{epw_num}_shapefile')
        df = pd.read_csv(f'/scratch/rswart/epws/{epw_num}.epw', skiprows=3241, nrows=384, header=None, usecols=[0,1,2,3,4,6,7,8,9,12,14,15,20,21,22], 
                         names=names)
        df['geometry'] = [gdf.geometry.values[0]] * len(df.index)
        return df

    import time
    old = time.time()

    tasks = [delayed(get_epw)(i) for i in files]
    gdf_list = compute(*tasks)

    print(f'done with this after {time.time()-old} seconds')

    big_df = pd.concat(gdf_list, ignore_index=True)
    print(f'done with big df after {time.time()-old} seconds')

    gdf = gpd.GeoDataFrame(big_df, crs='epsg:4326')
    gdf.to_file('/scratch/rswart/all_epws.shp')

