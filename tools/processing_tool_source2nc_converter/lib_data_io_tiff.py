"""
Class Features

Name:          lib_data_io_tiff
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
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

from tools.processing_tool_source2nc_converter.lib_info_args import logger_name

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
def read_data_tiff(file_name, var_scale_factor=1, var_type='float32', var_name=None, var_time=None, var_no_data=-9999.0,
                   coord_name_time='time', coord_name_geo_x='Longitude', coord_name_geo_y='Latitude',
                   dim_name_time='time', dim_name_geo_x='west_east', dim_name_geo_y='south_north',
                   dims_order=None,
                   decimal_round_data=7, flag_round_data=False,
                   decimal_round_geo=7, flag_round_geo=True):

    if dims_order is None:
        dims_order = [dim_name_geo_y, dim_name_geo_x, dim_name_time]

    if os.path.exists(file_name):
        # Open file tiff
        file_handle = rasterio.open(file_name)
        # Read file info and values
        file_bounds = file_handle.bounds
        file_res = file_handle.res
        file_transform = file_handle.transform
        file_nodata = file_handle.nodata
        file_data = file_handle.read()
        file_values = file_data[0, :, :]

        if file_nodata is None:
            file_nodata = var_no_data

        if flag_round_data:
            file_values = file_values.round(decimal_round_data)

        if var_type == 'float64':
            file_values = np.float64(file_values / var_scale_factor)
        elif var_type == 'float32':
            file_values = np.float32(file_values / var_scale_factor)
        else:
            log_stream.error(' ===> File type is not correctly defined.')
            raise NotImplemented('Case not implemented yet')

        if file_handle.crs is None:
            file_proj = proj_default_wkt
            log_stream.warning(' ===> Projection of tiff ' + file_name + ' not defined. Use constants settings.')
        else:
            file_proj = file_handle.crs.wkt
        file_geotrans = file_handle.transform

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

        lon = np.arange(center_left, center_right + np.abs(file_res[0] / 2), np.abs(file_res[0]), float)
        lat = np.arange(center_bottom, center_top + np.abs(file_res[1] / 2), np.abs(file_res[1]), float)
        lons, lats = np.meshgrid(lon, lat)

        if flag_round_geo:
            min_lon_round = round(np.min(lons), decimal_round_geo)
            max_lon_round = round(np.max(lons), decimal_round_geo)
            min_lat_round = round(np.min(lats), decimal_round_geo)
            max_lat_round = round(np.max(lats), decimal_round_geo)

            center_right_round = round(center_right, decimal_round_geo)
            center_left_round = round(center_left, decimal_round_geo)
            center_bottom_round = round(center_bottom, decimal_round_geo)
            center_top_round = round(center_top, decimal_round_geo)
        else:
            log_stream.error(' ===> Switch off the rounding of geographical dataset is not expected')
            raise NotImplemented('Case not implemented yet')

        assert min_lon_round == center_left_round
        assert max_lon_round == center_right_round
        assert min_lat_round == center_bottom_round
        assert max_lat_round == center_top_round

        var_geo_x_2d = lons
        var_geo_y_2d = np.flipud(lats)

        var_data = np.zeros(shape=[var_geo_x_2d.shape[0], var_geo_y_2d.shape[1], 1])
        var_data[:, :, :] = np.nan

        var_data[:, :, 0] = file_values

        var_attrs = {'nrows': var_geo_y_2d.shape[0], 'ncols': var_geo_x_2d.shape[1],
                     'nodata_value': file_nodata,
                     'xllcorner': file_transform[2],
                     'yllcorner': file_transform[5], 'cellsize': abs(file_transform[0]),
                     'proj': file_proj, 'transform': file_geotrans}

    else:
        log_stream.warning(' ===> File ' + file_name + ' not available in loaded datasets!')
        var_data = None

    if var_data is not None:

        if isinstance(var_time, pd.Timestamp):
            var_time = pd.DatetimeIndex([var_time])
        elif isinstance(var_time, pd.DatetimeIndex):
            pass
        else:
            log_stream.error(' ===> Time format is not allowed. Expected Timestamp or Datetimeindex')
            raise NotImplemented('Case not implemented yet')

        var_da = xr.DataArray(var_data, name=var_name, dims=dims_order,
                              coords={coord_name_time: ([dim_name_time], var_time),
                                      coord_name_geo_x: ([dim_name_geo_x], var_geo_x_2d[0, :]),
                                      coord_name_geo_y: ([dim_name_geo_y], var_geo_y_2d[:, 0])})
        var_da.attrs = var_attrs

    else:
        log_stream.warning(' ===> All filenames in the selected period are not available')
        var_da = None

    return var_da

# -------------------------------------------------------------------------------------
