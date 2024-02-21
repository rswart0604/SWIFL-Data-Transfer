import geopandas as gpd
# # import fiona
import matplotlib.pyplot as plt
import pandas as pd

bldg_fp = '/Users/ryanswart/Projects/PyProjects/DataTransfer/WRF_AutoBEM/sample_data_fromWRF_forAutoBEM/chi0_90m_coord2bldg_smc.csv'
weather_fp = '/Users/ryanswart/Projects/PyProjects/DataTransfer/WRF_AutoBEM/sample_data_fromWRF_forAutoBEM/chi_90m_grid.csv'
bldg_df = pd.read_csv(bldg_fp)
bldf_gdf = gpd.GeoDataFrame(bldg_df, geometry=gpd.points_from_xy(bldg_df.Lon, bldg_df.Lat))
weather_df = pd.read_csv(weather_fp)
weather_gdf = gpd.GeoDataFrame(weather_df, geometry=gpd.points_from_xy(weather_df.Lon, weather_df.Lat))
weather_gdf.plot()
bldf_gdf.plot()
# ax = weather_gdf.plot()
# bldf_gdf.plot(ax=ax)

foo = gpd.sjoin(weather_gdf, bldf_gdf)
print(foo.head())
print(foo.keys())
foo.plot()


plt.show()



#
# # Set filepath
# fp = "/Users/ryanswart/Projects/PyProjects/DataTransfer/WRF_AutoBEM/test_dir/ChicagoLoop_Morph1.shp"
#
# shapefile_gdf = gpd.read_file(fp, ignore_index=True)
#
# fp1 = "/Users/ryanswart/Projects/PyProjects/DataTransfer/WRF_AutoBEM/sample_data_fromWRF_forAutoBEM/chi_90m_grid.csv"
# df = pd.read_csv(fp1)
# chi_90m_grid = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Lon, df.Lat))
#
# # print(data.keys())
# # print(data.values[0])
# ax = shapefile_gdf.plot(color='red')
# chi_90m_grid.plot(ax=ax, markersize=2)
# print(f'{len(chi_90m_grid)=}')
# print(f'{len(shapefile_gdf)=}')
# # plt.show()
#
# chi_90m_grid.set_crs("epsg:4326")
# # wrf_grid_gdf.to_crs("epsg:4326")
# # wrf_grid_gdf.to_crs(crs={'init': 'epsg:4326'})
# # wrf_grid_gdf.to_crs(epsg='4326')
#
#
# foo = gpd.sjoin(chi_90m_grid, shapefile_gdf, op="within")
# # foo = shapefile_gdf.sjoin(chi_90m_grid, how='outer')
# print(foo.head())
# foo.to_csv('foo.csv')
#
# fp2 = "/Users/ryanswart/Projects/PyProjects/DataTransfer/WRF_AutoBEM/sample_data_fromWRF_forAutoBEM/chi0_90m_wrfcoord2bldg.csv"
# df = pd.read_csv(fp2)
# foo2 = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.coord_X, df.coord_Y))
# ax2 = shapefile_gdf.plot(color='red')
# foo2.plot(ax=ax2, markersize=3)
# fig, (ax1, ax2) = plt.subplots(1,2, figsize=(14, 6))
# foo2.plot(ax=ax1)
#
# # print([x for x in data])
# # data.plot()
# ax3 = shapefile_gdf.plot(color='red')
# foo.plot(ax=ax3, markersize=3)
# foo.plot(ax=ax2)
#
#
#
# plt.show()
