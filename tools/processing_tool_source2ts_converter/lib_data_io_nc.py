"""
Class Features

Name:          lib_data_io_nc
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""

#######################################################################################
# Libraries
import logging
import os
import time

import numpy as np
import xarray as xr
import pandas as pd

from copy import deepcopy
from netCDF4 import Dataset

from lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# method to read data netcdf
def read_data_nc(file_name, geo_ref_x=None, geo_ref_y=None, geo_ref_attrs=None,
                 var_coords=None, var_scale_factor=1, var_name=None, var_time=None, var_no_data=-9999.0,
                 coord_name_time='time', coord_name_geo_x='Longitude', coord_name_geo_y='Latitude',
                 dim_name_time='time', dim_name_geo_x='west_east', dim_name_geo_y='south_north',
                 dims_order=None, decimal_round=1, error_coords='ignore'):

    if var_coords is None:
        var_coords = {'x': 'Longitude', 'y': 'Latitude', 'time': 'time'}

    if dims_order is None:
        dims_order = [dim_name_geo_y, dim_name_geo_x, dim_name_time]

    var_data, file_attrs = None, None
    if os.path.exists(file_name):

        # Open file nc
        file_handle = xr.open_dataset(file_name)
        file_attrs = file_handle.attrs

        file_variables = list(file_handle.variables)
        file_dims = list(file_handle.dims)
        file_coords = list(file_handle.coords)

        idx_coords = {}
        for coord_key, coord_name in var_coords.items():
            if coord_name in file_coords:
                coord_idx = file_coords.index(coord_name)
            else:
                coord_idx = None
            idx_coords[coord_key] = coord_idx

        if var_name in file_variables:

            var_data = file_handle[var_name].values
            var_data = np.float32(var_data / var_scale_factor)

            if 'time' in list(idx_coords.keys()):
                if idx_coords['time'] is not None:
                    coord_name_time = file_coords[idx_coords['time']]
                    if file_handle[coord_name_time].size == 1:
                        if var_data.shape.__len__() < file_coords.__len__():
                            var_data = var_data[:, :, np.newaxis]
                        elif var_data.shape.__len__() == file_coords.__len__():
                            pass
                        else:
                            raise NotImplemented('File shape is greater than expected coords')
                    else:
                        raise NotImplemented('Time size is greater than 1')
                else:
                    raise IOError('Coord name "time" is not available')

            geo_data_x = None
            for step_coords_x in ['x', 'X']:
                if step_coords_x in idx_coords:
                    coord_name_x = file_coords[idx_coords[step_coords_x]]
                    geo_data_x = file_handle[coord_name_x].values
                    break
            if geo_data_x is None:
                raise IOError('Coord name "x" is not available or not defined')

            geo_data_y = None
            for step_coords_y in ['y', 'Y']:
                if step_coords_y in idx_coords:
                    coord_name_y = file_coords[idx_coords[step_coords_y]]
                    geo_data_y = file_handle[coord_name_y].values
                    break
            if geo_data_y is None:
                raise IOError('Coord name "y" is not available or not defined')

            geo_y_upper = geo_data_y[0, 0]
            geo_y_lower = geo_data_y[-1, 0]
            if geo_y_lower > geo_y_upper:
                geo_data_y = np.flipud(geo_data_y)
                var_data = np.flipud(var_data)

            if (geo_ref_x is not None) and (geo_ref_y is not None):
                geo_check_x, geo_check_y = np.meshgrid(geo_ref_x, geo_ref_y)

                geo_check_start_x = np.float32(round(geo_check_x[0, 0], decimal_round))
                geo_check_start_y = np.float32(round(geo_check_y[0, 0], decimal_round))
                geo_check_end_x = np.float32(round(geo_check_x[-1, -1], decimal_round))
                geo_check_end_y = np.float32(round(geo_check_y[-1, -1], decimal_round))

                geo_data_start_x = np.float32(round(geo_data_x[0, 0], decimal_round))
                geo_data_start_y = np.float32(round(geo_data_y[0, 0], decimal_round))
                geo_data_end_x = np.float32(round(geo_data_x[-1, -1], decimal_round))
                geo_data_end_y = np.float32(round(geo_data_y[-1, -1], decimal_round))

                # check coords
                if geo_check_start_x != geo_data_start_x:
                    if error_coords == 'ignore':
                        log_stream.warning(
                            ' ===> Variable :: geo x start [' + str(geo_check_start_x) +
                            '] != data x start [' + str(geo_data_start_x) + ']')
                    elif error_coords == 'raise':
                        log_stream.error(
                            ' ===> Variable :: geo x start [' + str(geo_check_start_x) +
                            '] != data x start [' + str(geo_data_start_x) + ']')
                        raise IOError('Check geo grid and data grid to control the coordinates')

                if geo_check_start_y != geo_data_start_y:
                    if error_coords == 'ignore':
                        log_stream.warning(
                            ' ===> Variable :: geo y start [' + str(geo_check_start_y) +
                            '] != data y start [' + str(geo_data_start_y) + ']')
                    elif error_coords == 'raise':
                        log_stream.error(
                            ' ===> Variable :: geo y start [' + str(geo_check_start_y) +
                            '] != data y start [' + str(geo_data_start_y) + ']')
                        raise IOError('Check geo grid and data grid to control the coordinates')

                if geo_check_end_x != geo_data_end_x:
                    if error_coords == 'ignore':
                        log_stream.warning(
                            ' ===> Variable :: geo x end [' + str(geo_check_end_x) +
                            '] != data x end [' + str(geo_data_end_x) + ']')
                    elif error_coords == 'raise':
                        log_stream.error(
                            ' ===> Variable :: geo x end [' + str(geo_check_end_x) +
                            '] != data x end [' + str(geo_data_end_x) + ']')
                        raise IOError('Check geo grid and data grid to control the coordinates')

                if geo_check_end_y != geo_data_end_y:
                    if error_coords == 'ignore':
                        log_stream.warning(
                            ' ===> Variable :: geo y end [' + str(geo_check_end_y) +
                            '] != data y end [' + str(geo_data_end_y) + ']')
                    elif error_coords == 'raise':
                        log_stream.error(
                            ' ===> Variable :: geo y end [' + str(geo_check_end_y) +
                            '] != data y end [' + str(geo_data_end_y) + ']')
                        raise IOError('Check geo grid and data grid to control the coordinates')

            else:
                log_stream.warning(' ===> GeoX and GeoY variables have not compared with a reference GeoX and GeoY')

        else:
            log_stream.warning(' ===> Variable ' + var_name + ' not available in loaded datasets!')
            var_data = None
    else:
        log_stream.warning(' ===> File ' + file_name + ' not available in loaded datasets!')
        var_data = None

    if var_data is not None:

        if var_time is not None:
            if isinstance(var_time, pd.Timestamp):
                var_time = pd.DatetimeIndex([var_time])
            elif isinstance(var_time, pd.DatetimeIndex):
                pass
            else:
                log_stream.error(' ===> Time format is not allowed. Expected Timestamp or Datetimeindex')
                raise NotImplemented('Case not implemented yet')

            var_da = xr.DataArray(var_data, name=var_name, dims=dims_order,
                                  coords={coord_name_time: ([dim_name_time], var_time),
                                          coord_name_geo_x: ([dim_name_geo_x], geo_data_x[0, :]),
                                          coord_name_geo_y: ([dim_name_geo_y], geo_data_y[:, 0])})

        elif var_time is None:

            var_da = xr.DataArray(var_data, name=var_name, dims=dims_order,
                                  coords={coord_name_geo_x: ([dim_name_geo_x], geo_data_x[0, :]),
                                          coord_name_geo_y: ([dim_name_geo_y], geo_data_y[:, 0])})

        if file_attrs and geo_ref_attrs:
            geo_attrs = {**file_attrs, **geo_ref_attrs}
        elif (not file_attrs) and geo_ref_attrs:
            geo_attrs = deepcopy(geo_ref_attrs)
        elif file_attrs and (not geo_ref_attrs):
            geo_attrs = deepcopy(file_attrs)
        else:
            geo_attrs = None

        if geo_attrs is not None:
            var_da.attrs = geo_attrs

    else:
        log_stream.warning(' ===> All filenames in the selected period are not available')
        var_da = None

    return var_da

# ----------------------------------------------------------------------------------------------------------------------
