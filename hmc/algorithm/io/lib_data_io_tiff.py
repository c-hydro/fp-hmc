"""
Class Features

Name:          lib_data_io_tiff
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210303'
Version:       '1.0.0'
"""

#######################################################################################
# Libraries
import logging
import os
import rasterio

import numpy as np
import xarray as xr
import pandas as pd

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Default settings
proj_default_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data
def read_data(file_name_list, var_name=None, var_time_start=None, var_time_end=None, var_time_freq='H',
              coord_name_time='time', coord_name_geo_x='Longitude', coord_name_geo_y='Latitude',
              dim_name_time='time', dim_name_geo_x='west_east', dim_name_geo_y='south_north',
              dims_order_3d=None, decimal_round_data=2, decimal_round_geo=7):

    if not isinstance(file_name_list, list):
        file_name_list = [file_name_list]

    if dims_order_3d is None:
        dims_order_3d = [dim_name_geo_y, dim_name_geo_x, dim_name_time]

    var_time_stamp = pd.date_range(start=var_time_start, end=var_time_end, freq=var_time_freq)
    var_datetime_idx = pd.DatetimeIndex(var_time_stamp)

    var_data_3d = None
    var_geox_2d = None
    var_geoy_2d = None
    for file_id, (file_name_step, datetime_idx_step) in enumerate(zip(file_name_list, var_datetime_idx)):

        if os.path.exists(file_name_step):
            # Open file tiff
            file_handle = rasterio.open(file_name_step)
            # Read file info and values
            file_bounds = file_handle.bounds
            file_res = file_handle.res
            file_transform = file_handle.transform
            file_data = file_handle.read()
            file_values = file_data[0, :, :]

            file_values = file_values.round(decimal_round_data)

            if file_handle.crs is None:
                file_proj = proj_default_wkt
                log_stream.warning(' ===> Projection of tiff ' + file_name_step + ' not defined. Use default settings.')
            else:
                file_proj = file_handle.crs.wkt
            file_geotrans = file_handle.transform

            # decimal_round_geo = 7

            file_dims = file_values.shape
            file_high = file_dims[0]
            file_wide = file_dims[1]

            center_right = file_bounds.right - (file_res[0] / 2)
            center_left = file_bounds.left + (file_res[0] / 2)
            center_top = file_bounds.top - (file_res[1] / 2)
            center_bottom = file_bounds.bottom + (file_res[1] / 2)

            if center_bottom > center_top:
                center_bottom_tmp = center_top
                center_top_tmp = center_bottom
                center_bottom = center_bottom_tmp
                center_top = center_top_tmp

                file_values = np.flipud(file_values)

            if (var_geox_2d is None) or (var_geoy_2d is None):
                lon = np.arange(center_left, center_right + np.abs(file_res[0] / 2), np.abs(file_res[0]), float)
                lat = np.arange(center_bottom, center_top + np.abs(file_res[1] / 2), np.abs(file_res[1]), float)
                lons, lats = np.meshgrid(lon, lat)

                min_lon_round = round(np.min(lons), decimal_round_geo)
                max_lon_round = round(np.max(lons), decimal_round_geo)
                min_lat_round = round(np.min(lats), decimal_round_geo)
                max_lat_round = round(np.max(lats), decimal_round_geo)

                center_right_round = round(center_right, decimal_round_geo)
                center_left_round = round(center_left, decimal_round_geo)
                center_bottom_round = round(center_bottom, decimal_round_geo)
                center_top_round = round(center_top, decimal_round_geo)

                assert min_lon_round == center_left_round
                assert max_lon_round == center_right_round
                assert min_lat_round == center_bottom_round
                assert max_lat_round == center_top_round

                var_geox_2d = lons
                var_geoy_2d = np.flipud(lats)

            if var_data_3d is None:
                var_data_3d = np.zeros(shape=[var_geox_2d.shape[0], var_geoy_2d.shape[1], var_time_stamp.__len__()])
                var_data_3d[:, :, :] = np.nan

            var_data_3d[:, :, file_id] = file_values

        else:
            log_stream.warning(' ===> File ' + file_name_step + ' not available in loaded datasets!')
            var_data_3d = None

    if var_data_3d is not None:
        # var_dset = xr.Dataset(coords={coord_name_time: ([dim_name_time], var_datetime_idx)})
        # var_dset.coords[coord_name_time] = var_dset.coords[coord_name_time].astype('datetime64[ns]')

        var_da = xr.DataArray(var_data_3d, name=var_name, dims=dims_order_3d,
                              coords={coord_name_time: ([dim_name_time], var_datetime_idx),
                                      coord_name_geo_x: ([dim_name_geo_y, dim_name_geo_x], var_geox_2d),
                                      coord_name_geo_y: ([dim_name_geo_y, dim_name_geo_x], var_geoy_2d)})

        # var_dset[var_name] = var_da

    else:
        log_stream.warning(' ===> All filenames in the selected period are not available')
        var_da = None
        var_datetime_idx = None
        var_geox_2d = None
        var_geoy_2d = None

    return var_da, var_datetime_idx, var_geox_2d, var_geoy_2d

# -------------------------------------------------------------------------------------
