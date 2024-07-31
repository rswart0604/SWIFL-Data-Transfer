import geopandas as gpd
import pandas as pd
import os
import numpy as np

from dask import delayed, compute
from dask.distributed import Client, LocalCluster

"""
this script is to take all of the result csvs from AutoBEM after it is run (OUTPUT FILES)
and put them into a shp file so that we can look at it.

every building has a single row
"""



if __name__ == '__main__':

    cluster = LocalCluster(n_workers=4, threads_per_worker=1)
    client = Client(cluster)

    files = np.loadtxt('/home/rswart/tiles.txt', dtype=int)

    def add_to_list(i):
        gdf = gpd.read_file(f'/scratch/rswart/shapefiles/{i}_shapefile')
        df = pd.read_csv(f'/scratch/frankli6/SWIFL_WRF_NP_Runs/{i}_WRF_NP.csv')
        df['geometry'] = [gdf.geometry.values[0]] * len(df.index) 
        return df

    import time
    old = time.time()

    tasks = [delayed(add_to_list)(i) for i in files]
    gdf_list = compute(*tasks)

    print(f'done with this after {time.time()-old} seconds')

    big_df = pd.concat(gdf_list, ignore_index=True)
    print(f'done with big df after {time.time()-old} seconds')
    
    gdf = gpd.GeoDataFrame(big_df, crs='epsg:4326')
    gdf.to_file('/scratch/rswart/all_attrs.shp')

