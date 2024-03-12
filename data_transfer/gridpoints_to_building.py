"""
this uses Arizona_MAv1_Select.csv (data.csv) and wrf data.
we plot the data.csv; plot the wrf data; match those (spatially join); and then summarize it

first we may want to filter Arizona_MAv1_Select.csv so we only deal with centroid and ID
"""

import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr


def summarize_AZ_data():
    fp_in = 'Arizona_MAv1_Select.csv'
    fp_out = 'data.csv'
    with open(fp_in) as infile:
        with open(fp_out, 'w') as outfile:
            outfile.write('lat,lon,id\n')
            for line in infile:
                if 'Centroid' in line:  # skip first line
                    continue
                vals = line.split(',')
                lat, lon = vals[1].split('/')
                outfile.write(f'{lat},{lon},{vals[-1]}')

def plot_AZ_data():
    fp = 'data.csv'
    df = pd.read_csv(fp)
    print('done0')
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['lat'], df['lon']))
    print('done1')
    # gdf.plot()
    print(gdf)




if __name__ == '__main__':
    # summarize_AZ_data()
    plot_AZ_data()
    plt.show()