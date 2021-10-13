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

from netCDF4 import Dataset

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to write data netcdf
def write_data_nc(file_name, file_obj_data, file_obj_dims_def, file_obj_dims_list,
                  file_obj_attrs, file_format='NETCDF4_CLASSIC'):

    # Open file handle
    file_handle = Dataset(file_name, 'w', format=file_format)

    # Cycle on file dimension(s)
    dim_obj_collections = {}
    for dim_key, dim_value in file_obj_dims_def.items():
        if dim_key not in list(file_handle.dimensions.items()):
            dim_obj_step = file_handle.createDimension(dim_key, dim_value)
            dim_obj_collections[dim_key] = dim_obj_step

    # Cycle on file attribute(s)
    for attr_key, attr_value in file_obj_attrs.items():
        file_handle.setncattr(attr_key, attr_value)
    file_handle.filedate = 'Created ' + time.ctime(time.time())

    for data_key, data_values in file_obj_data.items():

        if data_key in list(file_obj_dims_list.keys()):

            dim_values = file_obj_dims_list[data_key]

            if data_values.ndim == 2:
                data_dim_x = dim_values[1]
                data_dim_y = dim_values[0]

                file_var = file_handle.createVariable(data_key, np.float32,
                                                      (data_dim_y, data_dim_x,), zlib=True)

                file_var[:, :] = np.transpose(np.rot90(data_values, -1))

            elif data_values.ndim == 3:
                data_dim_x = dim_values[1]
                data_dim_y = dim_values[0]
                data_dim_time = dim_values[2]

                file_var = file_handle.createVariable(data_key, np.float32,
                                                      (data_dim_time, data_dim_y, data_dim_x,), zlib=True)

                file_var[:, :, :] = np.transpose(np.rot90(data_values, -1))

            else:
                log_stream.warning(' ===> Datasets dimensions for ' +
                                   data_key + ' is not allowed. Only 2D or 3D arrays are implemented.')

    file_handle.close()

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data netcdf
def read_data_nc(file_name, geo_ref_x, geo_ref_y, geo_ref_attrs,
                 var_coords=None, var_scale_factor=1, var_name=None, var_time=None, var_no_data=-9999.0,
                 coord_name_time='time', coord_name_geo_x='Longitude', coord_name_geo_y='Latitude',
                 dim_name_time='time', dim_name_geo_x='west_east', dim_name_geo_y='south_north',
                 dims_order=None, decimal_round=4):

    if var_coords is None:
        var_coords = {'x': 'Longitude', 'y': 'Latitude', 'time': 'time'}

    if dims_order is None:
        dims_order = [dim_name_geo_y, dim_name_geo_x, dim_name_time]

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

            if idx_coords['x'] is not None:
                coord_name_x = file_coords[idx_coords['x']]
                geo_data_x = file_handle[coord_name_x].values
            else:
                raise IOError('Coord name "x" is not available')

            if idx_coords['y'] is not None:
                coord_name_y = file_coords[idx_coords['y']]
                geo_data_y = file_handle[coord_name_y].values
            else:
                raise IOError('Coord name "y" is not available')

            geo_y_upper = geo_data_y[0, 0]
            geo_y_lower = geo_data_y[-1, 0]
            if geo_y_lower > geo_y_upper:
                geo_data_y = np.flipud(geo_data_y)
                var_data = np.flipud(var_data)

            geo_check_x, geo_check_y = np.meshgrid(geo_ref_x, geo_ref_y)

            geo_check_start_x = np.float32(round(geo_check_x[0, 0], decimal_round))
            geo_check_start_y = np.float32(round(geo_check_y[0, 0], decimal_round))
            geo_check_end_x = np.float32(round(geo_check_x[-1, -1], decimal_round))
            geo_check_end_y = np.float32(round(geo_check_y[-1, -1], decimal_round))

            geo_data_start_x = np.float32(round(geo_data_x[0, 0], decimal_round))
            geo_data_start_y = np.float32(round(geo_data_y[0, 0], decimal_round))
            geo_data_end_x = np.float32(round(geo_data_x[-1, -1], decimal_round))
            geo_data_end_y = np.float32(round(geo_data_y[-1, -1], decimal_round))

            assert geo_check_start_x == geo_data_start_x, ' ===> Variable geo x start != Reference geo x start'
            assert geo_check_start_y == geo_data_start_y, ' ===> Variable geo y start != Reference geo y start'
            assert geo_check_end_x == geo_data_end_x, ' ===> Variable geo x end != Reference geo x end'
            assert geo_check_end_y == geo_data_end_y, ' ===> Variable geo y end != Reference geo y end'

        else:
            log_stream.warning(' ===> Variable ' + var_name + ' not available in loaded datasets!')
            var_data = None
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
                                      coord_name_geo_x: ([dim_name_geo_x], geo_data_x[0, :]),
                                      coord_name_geo_y: ([dim_name_geo_y], geo_data_y[:, 0])})

        if geo_ref_attrs is not None:
            var_da.attrs = geo_ref_attrs

    else:
        log_stream.warning(' ===> All filenames in the selected period are not available')
        var_da = None

    return var_da

# -------------------------------------------------------------------------------------
