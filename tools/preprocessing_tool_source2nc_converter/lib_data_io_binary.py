"""
Library Features:

Name:          lib_data_io_binary
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""
#######################################################################################
# Library
import logging
import os
import struct

from copy import deepcopy

import numpy as np
import pandas as pd
import xarray as xr

from tools.preprocessing_tool_source2nc_converter.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
#######################################################################################


# --------------------------------------------------------------------------------
# Method to get size of binary file
def search_geo_reference(file_name, info_dict, tag_geo_reference=None,
                         tag_cols='ncols', tag_rows='nrows', scale_factor=4):

    file_handle = open(file_name, 'rb')
    file_stream = file_handle.read(-1)
    straem_n = file_stream.__len__()

    data_tag = None
    for info_key, info_fields in info_dict.items():
        data_n = int(info_fields[tag_cols]) * int(info_fields[tag_rows]) * scale_factor
        if data_n == straem_n:
            data_info = info_fields
            data_tag = info_key
            break

    file_handle.close()

    assert data_tag == tag_geo_reference, " ===> Geographical reference set and found are not equal. " \
                                          "Check your settings and datasets"

    return data_tag
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Method to read 2d variable in binary format (saved as 1d integer array)
def read_data_binary(file_name, var_geo_x, var_geo_y, var_geo_attrs=None, var_format='i', var_scale_factor=10,
                     var_name=None, var_time=None, var_geo_1d=True,
                     coord_name_geo_x='west_east', coord_name_geo_y='south_north', coord_name_time='time',
                     dim_name_geo_x='west_east', dim_name_geo_y='south_north', dim_name_time='time',
                     dims_order=None):

    if dims_order is None:
        dims_order = [dim_name_geo_y, dim_name_geo_x, dim_name_time]

    if os.path.exists(file_name):

        # Open file handle
        file_handle = open(file_name, 'rb')
        rows = var_geo_y.shape[0]
        cols = var_geo_x.shape[0]

        # Values shape (1d)
        var_n = rows * cols
        # Values format
        data_format = var_format * var_n
        # Open and read binary file
        data_stream = file_handle.read(-1)
        array_data = struct.unpack(data_format, data_stream)

        # Close file handle
        file_handle.close()

        # Reshape binary file in Fortran order and scale Data (float32)
        file_values = np.reshape(array_data, (rows, cols), order='F')
        file_values = np.float32(file_values / var_scale_factor)

        if var_geo_1d:
            var_geo_x_2d, var_geo_y_2d = np.meshgrid(var_geo_x, var_geo_y)
        else:
            var_geo_x_2d = var_geo_x
            var_geo_y_2d = var_geo_y

        geo_y_upper = var_geo_y_2d[0, 0]
        geo_y_lower = var_geo_y_2d[-1, 0]
        if geo_y_lower > geo_y_upper:
            var_geo_y_2d = np.flipud(var_geo_y_2d)

        file_dims = file_values.shape
        file_high = file_dims[0]
        file_wide = file_dims[1]

        var_data = np.zeros(shape=[var_geo_x_2d.shape[0], var_geo_y_2d.shape[1], 1])
        var_data[:, :, :] = np.nan

        var_data[:, :, 0] = file_values

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
        if var_geo_attrs is not None:
            var_da.attrs = var_geo_attrs

    else:
        log_stream.warning(' ===> All filenames in the selected period are not available')
        var_da = None

    return var_da
# -------------------------------------------------------------------------------------
