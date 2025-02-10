import numpy as np
import cartopy.crs as ccrs


def split_point(x, deviation=0.03):
    delta = (2 * np.random.rand(4) - 1) * deviation * x
    new_points = x + delta
    correction = (4 * x - np.sum(new_points)) / 4
    new_points += correction
    return new_points.reshape(2 ,2)

# get x,y coords and return deltas in each dir
latlonproj = ccrs.PlateCarree()
def split_loc(loc,dist,proj,is_lon):
    if is_lon:
        idx = 0
    else:
        idx = 1
    ul = latlonproj.transform_point(loc[0] - dist, loc[1] - dist, proj)[idx]
    ur = latlonproj.transform_point(loc[0] + dist, loc[1] - dist, proj)[idx]
    ll = latlonproj.transform_point(loc[0] - dist, loc[1] + dist, proj)[idx]
    lr = latlonproj.transform_point(loc[0] - dist, loc[1] + dist, proj)[idx]
    return np.array([ul,ur,ll,lr]).reshape(2,2)
