"""
Library Features:

Name:          lib_utils_geo
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#################################################################################
# Libraries
import logging
import rasterio

import numpy as np

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#################################################################################


# -------------------------------------------------------------------------------------
# Method to get a raster ascii file
def get_raster(filename_reference):

    dset = rasterio.open(filename_reference)
    bounds = dset.bounds
    res = dset.res
    transform = dset.transform
    data = dset.read()
    values = data[0, :, :]

    decimal_round = 7

    center_right = bounds.right - (res[0] / 2)
    center_left = bounds.left + (res[0] / 2)
    center_top = bounds.top - (res[1] / 2)
    center_bottom = bounds.bottom + (res[1] / 2)

    lon = np.arange(center_left, center_right + np.abs(res[0] / 2), np.abs(res[0]), float)
    lat = np.arange(center_bottom, center_top + np.abs(res[0] / 2), np.abs(res[1]), float)
    lons, lats = np.meshgrid(lon, lat)

    min_lon_round = round(np.min(lons), decimal_round)
    max_lon_round = round(np.max(lons), decimal_round)
    min_lat_round = round(np.min(lats), decimal_round)
    max_lat_round = round(np.max(lats), decimal_round)

    center_right_round = round(center_right, decimal_round)
    center_left_round = round(center_left, decimal_round)
    center_bottom_round = round(center_bottom, decimal_round)
    center_top_round = round(center_top, decimal_round)

    assert min_lon_round == center_left_round
    assert max_lon_round == center_right_round
    assert min_lat_round == center_bottom_round
    assert max_lat_round == center_top_round

    lats = np.flipud(lats)

    obj = {'values': values, 'longitude': lons, 'latitude': lats,
           'transform': transform, 'bbox': [bounds.left, bounds.bottom, bounds.right, bounds.top],
           'bb_left': bounds.left, 'bb_right': bounds.right,
           'bb_top': bounds.top, 'bb_bottom': bounds.bottom,
           'res_lon': res[0], 'res_lat': res[1]}

    return obj
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compute corrivation time
def compute_corrivation_time(geo_values, geo_x, geo_y, cellsize_x, cellsize_y):

    # Dynamic values
    r = 6378388  # (Radius)
    e = 0.00672267  # (Ellipsoid)

    # dx = (R * cos(lat)) / (sqrt(1 - e2 * sqr(sin(lat)))) * PI / 180
    dx_2d = (r * np.cos(np.abs(geo_y) * np.pi / 180)) / \
            (np.sqrt(1 - e * np.sqrt(np.sin(np.abs(geo_y) * np.pi / 180)))) * np.pi / 180

    # dy = (R * (1 - e2)) / pow((1 - e2 * sqr(sin(lat))),1.5) * PI / 180
    dy_2d = (r * (1 - e)) / np.power((1 - e * np.sqrt(np.sin(np.abs(geo_y) / 180))), 1.5) * np.pi / 180

    # Area in m^2
    area_2d = ((dx_2d / (1 / cellsize_x)) * (dy_2d / (1 / cellsize_y)))  # [m^2]

    # Area, Mean Dx and Dy values (meters)
    dx_avg = np.sqrt(np.nanmean(area_2d))
    dy_avg = np.sqrt(np.nanmean(area_2d))

    # Compute domain pixels and area
    pixels_n = np.sum(np.isfinite(geo_values))
    area_tot = float(pixels_n) * dx_avg * dy_avg / 1000000

    # Corrivation time [hour]
    tc = np.int(0.27 * np.sqrt(0.6 * area_tot) + 0.25)

    return tc
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to clip data 2D/3D using a min/max threshold(s) and assign a missing value
def clip_map(map, valid_range=None, missing_value=None):

    # Set variable valid range
    if valid_range is None:
        valid_range = [None, None]

    if valid_range is not None:
        if valid_range[0] is not None:
            valid_range_min = float(valid_range[0])
        else:
            valid_range_min = None
        if valid_range[1] is not None:
            valid_range_max = float(valid_range[1])
        else:
            valid_range_max = None
        # Set variable missing value
        if missing_value is None:
            missing_value_min = valid_range_min
            missing_value_max = valid_range_max
        else:
            missing_value_min = missing_value
            missing_value_max = missing_value

        # Apply min and max condition(s)
        if valid_range_min is not None:
            map = map.where(map >= valid_range_min, missing_value_min)
        if valid_range_max is not None:
            map = map.where(map <= valid_range_max, missing_value_max)

        return map
    else:
        return map

# -------------------------------------------------------------------------------------
