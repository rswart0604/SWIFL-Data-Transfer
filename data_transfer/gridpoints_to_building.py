"""
this uses Arizona_MAv1_Select.csv (bldg_data.csv) and wrf data.
we plot the bldg_data.csv; plot the wrf data; match those (spatially join); and then summarize it

first we may want to filter Arizona_MAv1_Select.csv so we only deal with centroid and ID

get the Arizona_MAv1_Select.csv from https://data.ess-dive.lbl.gov/view/doi:10.15485/2212792
"""
import time

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap


# summarize Arizona_MAv1_Select.csv into bldg_data.csv
# just extracts the lats and lons and the ids of the buildings
def summarize_AZ_data():
    fp_in = 'Arizona_MAv1_Select.csv'
    fp_out = 'bldg_data.csv'
    with open(fp_in) as infile:
        with open(fp_out, 'w') as outfile:
            outfile.write('lat,lon,id\n')
            for line in infile:
                if 'Centroid' in line:  # skip first line
                    continue
                vals = line.split(',')
                lat, lon = vals[1].split('/')
                outfile.write(f'{lat},{lon},{vals[-1]}')


# plot the lats and lons and ids of buildings
def get_bldg_data(ax=None):
    fp = 'bldg_data.csv'
    df = pd.read_csv(fp)
    df = df[(-111 >= df['lon']) & (df['lon'] >= -113.5)]
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['lon'], df['lat']), crs="EPSG:3857")
    print('done1')
    if ax:
        gdf.plot(ax=ax, markersize=.0005)
    return gdf


# plot the wrf coordinates (with the info)
# todo right now from a csv. want to do this from netcdf
def get_wrf_data(ax=None):
    fp = 'wrf.csv'
    df = pd.read_csv(fp)
    df.drop_duplicates(subset='wrfid', keep='first', inplace=True)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:3857"
    )
    return gdf

# this is only for if you want to do partitioning with multiprocessing
def do_join(partition: gpd.GeoDataFrame):
    wrf = get_wrf_data()
    print('heya!')
    foo = partition.sjoin_nearest(wrf, max_distance=2000)
    return foo


def match(fp='matched.csv'):
    bldg = get_bldg_data()
    wrf = get_wrf_data()
    foo = bldg.sjoin_nearest(wrf, how='left', max_distance=2000)
    foo.to_csv(fp)





# if __name__ == '__main__':




    # from multiprocessing import Pool
    # partitions = []
    # size = len(bldg) // 20
    # start = 0
    # for i in range(10):
    #     start_idx = i * size
    #     end_idx = (i + 1) * size if i < 7 else len(bldg)
    #     partitions.append(bldg.iloc[start_idx:end_idx])
    # print(f'{len(a)=}')
    # print(f'{len(wrf)=}')
    # bar = a.sjoin_nearest(wrf, how='left', max_distance=2000)
    # print(bar)
    # bar.to_csv('new_matched_stuff.csv')

    # print('made my partitions')
    # with Pool(processes=10) as p:
    #     results = p.map(do_join, partitions)
    #
    # foo = pd.concat(results)
    # print(foo)




# match the data!
# from multiprocessing import Pool
# if __name__ == '__main__':
#     bldg = get_bldg_data()
#     wrf = get_wrf_data()
#     with Pool(processes=8) as p:















# import dask_geopandas
# fp = 'wrf.csv'
# df = pd.read_csv(fp)
# gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
# # print(type(gdf))
# foo = dask_geopandas.from_geopandas(gdf, npartitions=4)
# print(foo)