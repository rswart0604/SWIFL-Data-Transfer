import random

import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(12,6))

### this plots the wrf coords as seen in chi0_90m_wrfcoord2bldg and compares to the shapefile
fp = '../WRF_AutoBEM/sample_data_fromWRF_forAutoBEM/chi0_90m_wrfcoord2bldg.csv'
df = pd.read_csv(fp)
df['coord'] = df['coord'].str.split(';')
df = df.explode('coord')
coord = df['coord']
coord_list = coord.str.split(' ')
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy([x[1] for x in coord_list], [x[0] for x in coord_list]))
# print(gdf)
fp = "../WRF_AutoBEM/test_dir/ChicagoLoop_Morph1.shp"
shapefile_gdf = gpd.read_file(fp, ignore_index=True)
shapefile_gdf.plot(ax=ax1, color='red')
gdf.plot(ax=ax1, markersize=2)  # plot all of the wrf grid coords for chi0_90m_wrfcoord2bldg
###

### this plots what every single wrf point looks like compared to shapefile
fp = '../WRF_AutoBEM/sample_data_fromWRF_forAutoBEM/chi_90m_grid.csv'
df = pd.read_csv(fp)
chi_90m_grid = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Lon, df.Lat))
shapefile_gdf.plot(ax=ax2, color='red')
chi_90m_grid.plot(ax=ax2, markersize=2)
###

### this plots what i am able to come up with
# i am only using chi_90m_grid.csv (wrf grid) and the shapefile (building shapes)
fp = '../WRF_AutoBEM/sample_data_fromWRF_forAutoBEM/chi_90m_grid.csv'
df = pd.read_csv(fp)
wrf_grid = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Lon, df.Lat))

output = gpd.sjoin_nearest(shapefile_gdf, wrf_grid)
ax = output.plot(column='OBJECTID', cmap='OrRd')
output.to_csv('sjoin_nearest.csv')

new = output.set_geometry(gpd.points_from_xy(output.Lon, output.Lat))
new.plot(ax=ax, column='OBJECTID', cmap='OrRd', markersize=12, edgecolor='black', linewidth=.35)
###





plt.show()
