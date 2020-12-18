"""
Class Features

Name:          lib_data_io_nc
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Libraries
import logging
import os
import netCDF4
import time
import re

import numpy as np
import xarray as xr
import pandas as pd

from copy import deepcopy

from hmc.algorithm.io.lib_data_io_generic import reshape_var3d, create_darray_3d, create_darray_2d
from hmc.algorithm.default.lib_default_args import logger_name, time_units, time_calendar, time_format_algorithm

from hmc.algorithm.utils.lib_utils_system import create_folder

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to write collections
def write_collections(file_name, file_data, file_time, file_attrs=None):

    time_date_list = []
    time_str_list = []
    for time_stamp_step in file_time:
        time_str_step = time_stamp_step.strftime(format=time_format_algorithm)
        time_str_list.append(time_str_step)
        time_date_step = time_stamp_step.to_pydatetime()
        time_date_list.append(time_date_step)

    # File operation(s)
    file_handle = netCDF4.Dataset(file_name, 'w')
    file_handle.createDimension('time', len(file_time))

    # File attribute(s)
    if file_attrs is not None:
        for attr_key, attr_value in file_attrs.items():
            file_handle.setncattr(attr_key, attr_value)

    # Time information
    file_time_num = file_handle.createVariable(varname='time', dimensions=('time',), datatype='float32')
    file_time_num[:] = netCDF4.date2num(time_date_list, units=time_units, calendar=time_calendar)
    file_time_str = file_handle.createVariable(varname='times', dimensions=('time',), datatype='str')
    file_time_str[:] = np.array(time_str_list, dtype=object)

    # Add file creation date
    file_handle.file_date = 'Created ' + time.ctime(time.time())

    for file_key, file_dict in file_data.items():

        file_values = list(file_dict.values())

        if isinstance(file_values[0], str):

            file_data = np.array(file_values, dtype=object)
            file_var = file_handle.createVariable(varname=file_key, dimensions=('time',), datatype='str')

        elif isinstance(file_values[0], (int, float)):

            file_data = file_values
            file_var = file_handle.createVariable(varname=file_key, dimensions=('time',), datatype='f4')

        else:
            log_stream.error(' ===> Variable format in collections is not allowed!')
            raise IOError('Bad format of array')

        file_var[:] = file_data

    file_handle.close()

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data
def read_data(file_name_list, var_name=None, var_time_start=None, var_time_end=None, var_time_freq='H',
              coord_name_time='time', coord_name_geo_x='Longitude', coord_name_geo_y='Latitude',
              dim_name_time='time', dim_name_geo_x='west_east', dim_name_geo_y='south_north'):

    # File n
    file_n = file_name_list.__len__()

    if var_name is None:
        log_stream.error(' ===> Variable name is undefined!')
        raise IOError('Variable name is a mandatory argument!')
    else:
        if isinstance(var_name, list):
            var_name = var_name[0]

    file_check_list = []
    for file_name_step in file_name_list:
        if os.path.exists(file_name_step):
            file_check_list.append(True)
        else:
            file_check_list.append(False)
    file_check = any(el for el in file_check_list)

    # Open datasets
    if file_check:

        if file_n == 1:

            if os.path.exists(file_name_list[0]):
                try:
                    dst_tmp = xr.open_dataset(file_name_list[0])
                except BaseException as base_exp:
                    log_stream.warning(' ===> Exception ' + str(base_exp) + ' occurred in reading netcdf file list')
                    dst_tmp = xr.open_dataset(file_name_step, decode_times=False)

                    file_group_match = re.search('\d{4}\d{2}\d{2}\d{2}\d{2}', os.path.split(file_name_step)[1])
                    file_time_match = file_group_match.group()
                    file_timestamp_match = pd.Timestamp(file_time_match)
                    file_datetimeindex_match = pd.DatetimeIndex([file_timestamp_match])

                    log_stream.warning(
                        ' ===> Automatic datetime detection for filename ' + os.path.split(file_name_step)[1]
                        + ' return the following filetime: ' + str(file_timestamp_match))

                    if 'time' in list(dst_tmp.dims):
                        dst_tmp = dst_tmp.squeeze(dim_name_time)

                    dst_tmp['time'] = file_datetimeindex_match
                    dst_tmp = dst_tmp.set_coords('time')
                    dst_tmp = dst_tmp.expand_dims('time')

                if var_name == 'ALL':
                    var_list = list(dst_tmp.data_vars)
                    dst = dst_tmp
                elif var_name in list(dst_tmp.data_vars):
                    var_list = [var_name]
                    dst = dst_tmp[var_list]
                else:
                    log_stream.warning(' ===> Variable ' + var_name + ' not available in loaded datasets!')
                    var_list = None
                    dst = None

            else:
                log_stream.warning(' ===> File ' + file_name_list[0] + ' not available in loaded datasets!')

        elif file_n > 1:

            datetime_tmp = pd.date_range(start=var_time_start, end=var_time_end, freq=var_time_freq)
            datetime_idx_select = pd.DatetimeIndex(datetime_tmp)

            try:
                dst_tmp = xr.open_mfdataset(file_name_list, combine='by_coords')
            except BaseException as base_exp:

                log_stream.warning(' ===> Exception ' + str(base_exp) + ' occurred in reading netcdf file list')
                dst_tmp = None
                for file_name_step, datetime_idx_step in zip(file_name_list, datetime_idx_select):

                    if os.path.exists(file_name_step):

                        dst_step = xr.open_dataset(file_name_step, decode_times=False)

                        if 'time' in list(dst_step.dims):
                            dst_step = dst_step.squeeze(dim_name_time)

                        dst_step['time'] = datetime_idx_step
                        dst_step = dst_step.set_coords('time')
                        dst_step = dst_step.expand_dims('time')
                        if dst_tmp is None:
                            dst_tmp = deepcopy(dst_step)
                        else:
                            dst_tmp = dst_tmp.combine_first(deepcopy(dst_step))
                    else:
                        log_stream.warning(' ===> File ' + file_name_step + ' not available in loaded datasets!')
                        # raise IOError('File not found') # da rivedere nel caso ci siano dati non continui (tipo updating)

            if var_name == 'ALL':
                var_list = list(dst_tmp.data_vars)
                dst = dst_tmp
            elif var_name in list(dst_tmp.data_vars):
                var_list = [var_name]
                dst = dst_tmp[var_list]
            else:
                log_stream.warning(' ===> Variable ' + var_name + ' not available in loaded datasets!')
                var_list = None
                dst = None
        else:
            log_stream.error(' ===> Filename list is not available!')
            raise IOError('Filename list is null')

        # Check datasets
        if dst is not None:

            # Get dimensions and coordinates
            dst_list_coords = list(dst.coords)

            # Get time, geo x and geo y
            if coord_name_time in dst_list_coords:
                da_time = dst[coord_name_time]
            else:
                # log_stream.warning(' ===> Time dimension name is not in the variables list of nc file')
                if var_time_start == var_time_end:
                    da_time = pd.DatetimeIndex([var_time_end])
                else:
                    log_stream.error(' ===> Time indexes are not implemented for this case')
                    raise IOError(' ===> Case not implemented yet!')

            if coord_name_geo_x not in dst_list_coords:
                coord_name_geo_x_list = ['Longitude', 'longitude', 'lon', 'Lon', 'LON']
                for coord_name_geo_x_tmp in coord_name_geo_x_list:
                    if coord_name_geo_x_tmp in dst_list_coords:
                        log_stream.warning(' ===> GeoX coord name used ' + coord_name_geo_x +
                                           ' but found ' + coord_name_geo_x_tmp + ' in collected datasets')
                        coord_name_geo_x = coord_name_geo_x_tmp
                        break

            if coord_name_geo_x in dst_list_coords:
                da_geo_x_tmp = dst[coord_name_geo_x]
                if dim_name_time in list(da_geo_x_tmp.dims):
                    da_geo_x = da_geo_x_tmp.squeeze(dim_name_time)
                else:
                    da_geo_x = da_geo_x_tmp
            else:
                log_stream.error(' ===> GeoX dimension name is not in the variables list of nc file')
                raise IOError(' ===> Check the GeoX dimension!')

            if coord_name_geo_y not in dst_list_coords:
                coord_name_geo_y_list = ['Latitude', 'latitude', 'lat', 'Lat', 'LAT']
                for coord_name_geo_y_tmp in coord_name_geo_y_list:
                    if coord_name_geo_y_tmp in dst_list_coords:
                        log_stream.warning(' ===> GeoY coord name used ' + coord_name_geo_y +
                                           ' but found ' + coord_name_geo_y_tmp + ' in collected datasets')
                        coord_name_geo_y = coord_name_geo_y_tmp
                        break

            if coord_name_geo_y in dst_list_coords:
                da_geo_y_tmp = dst[coord_name_geo_y]
                if dim_name_time in list(da_geo_y_tmp.dims):
                    da_geo_y = da_geo_y_tmp.squeeze(dim_name_time)
                else:
                    da_geo_y = da_geo_y_tmp
            else:
                log_stream.error(' ===> GeoY dimension name is not in the variables list of nc file')
                raise IOError(' ===> Check the GeoY dimension!')

            if da_time is not None:
                time_stamp_period = []
                for time_step in da_time.values:
                    timestamp_step = pd.to_datetime(time_step, format='%Y-%m-%d_%H:%M:%S')
                    timestamp_step = timestamp_step.round('H')
                    time_stamp_period.append(timestamp_step)
                datetime_idx = pd.DatetimeIndex(time_stamp_period)
            else:
                datetime_idx = None

            if var_name == 'ALL':

                geo_y_upper = da_geo_y.values[0, 0]
                geo_y_lower = da_geo_y.values[-1, 0]
                if geo_y_lower > geo_y_upper:
                    values_geo_y = np.flipud(da_geo_y.values)
                    values_geo_x = da_geo_x.values

                    da_var = None
                    dim_name_select = None
                    coord_name_select = None
                    for var_name in dst.data_vars:
                        var_tmp = dst[var_name].values
                        var_dims = list(dst.dims.items())

                        if var_tmp.ndim == 2:
                            var_data = np.flipud(var_tmp)
                            datetime_idx_select = datetime_idx
                            dim_name_select = 'time'
                            coord_name_select = 'time'
                        elif var_tmp.ndim == 3:
                            var_tmp = reshape_var3d(var_tmp)

                            for dim_step in var_dims:
                                dim_name = dim_step[0]
                                dim_value = dim_step[1]
                                if dim_value == var_tmp.shape[2]:
                                    dim_name_select = dim_name
                                    coord_name_select = dim_name
                                    break
                                else:
                                    dim_name_select = None

                            if dim_name_select is None:
                                var_data = np.flipud(var_tmp[:, :, 0])
                                datetime_idx_select = datetime_idx
                                dim_name_select = 'time'
                                coord_name_select = 'time'
                            else:
                                datetime_tmp = pd.date_range(end=var_time_end, periods=var_tmp.shape[2],
                                                             freq=var_time_freq)
                                datetime_idx_select = pd.DatetimeIndex(datetime_tmp)
                                var_data = np.flipud(var_tmp)

                        elif var_tmp.ndim == 1:
                            if var_name != 'times':
                                log_stream.error(' ===> Variable ' + var_name + ' with 1 dimension')
                                raise IOError(' ===> Variable are expected to have 2 or 3 dimensions')
                            elif var_name == 'times':
                                var_data = var_tmp
                        else:
                            if var_name != 'times':
                                log_stream.error(' ===> Variable ' + var_name + ' with 1 dimension')
                                raise IOError(' ===> Variable are expected to have 2 or 3 dimensions')
                            elif var_name == 'times':
                                var_data = var_tmp

                        if var_data.shape.__len__() == 2:
                            da_tmp = create_darray_2d(var_data, values_geo_x, values_geo_y, time=datetime_idx_select,
                                                      coord_name_time=coord_name_select,
                                                      coord_name_x=coord_name_geo_x, coord_name_y=coord_name_geo_y,
                                                      dim_name_time=dim_name_select,
                                                      dim_name_x=dim_name_geo_x, dim_name_y=dim_name_geo_y,
                                                      dims_order=[dim_name_geo_y, dim_name_geo_x, dim_name_select])
                        elif var_data.shape.__len__() == 3:
                            da_tmp = create_darray_3d(var_data,
                                                      datetime_idx_select, values_geo_x, values_geo_y,
                                                      coord_name_time=coord_name_select,
                                                      coord_name_x=coord_name_geo_x, coord_name_y=coord_name_geo_y,
                                                      dim_name_time=dim_name_select,
                                                      dim_name_x=dim_name_geo_x, dim_name_y=dim_name_geo_y,
                                                      dims_order=[dim_name_geo_y, dim_name_geo_x, dim_name_select])

                        elif var_data.shape.__len__() == 1:
                            if var_name != 'times':
                                log_stream.error(' ===> Only variable times can be 1-dimension')
                                raise IOError(' ===> Case not implemented')
                            elif var_name == 'times':
                                da_tmp = None
                        else:
                            if var_name != 'times':
                                log_stream.error(' ===> Only variable times can be 1-dimension')
                                raise IOError(' ===> Case not implemented')
                            elif var_name == 'times':
                                da_tmp = None

                        if da_tmp is not None:
                            if da_var is None:
                                da_var = da_tmp.to_dataset(name=var_name)
                            else:
                                da_tmp = da_tmp.to_dataset(name=var_name)
                                da_var = da_var.merge(da_tmp, join='right')

                else:

                    values_geo_y = da_geo_y.values
                    values_geo_x = da_geo_x.values
                    da_var = dst

            else:
                da_raw = dst[var_name]
                da_raw_dims = da_raw.dims

                if 'time' in da_raw_dims:

                    dims_list = list(da_raw_dims)
                    time_idx = dims_list.index('time')

                    dim = da_raw_dims[time_idx].lower()
                    if dim == 'time':
                        values_raw = da_raw.values

                        if time_idx == 0:
                            values_reshape = reshape_var3d(values_raw)
                        elif time_idx == 2:
                            values_reshape = values_raw
                        else:
                            log_stream.error(' ===> Time idx ' + str(time_idx) + ' is not allowed in 3d variables')
                            raise NotImplementedError(' ===> Case not implemented')

                        geo_y_upper = da_geo_y.values[0, 0]
                        geo_y_lower = da_geo_y.values[-1, 0]
                        if geo_y_lower > geo_y_upper:
                            values_reshape_flip = np.flipud(values_reshape)
                            values_geo_y = np.flipud(da_geo_y.values)
                            values_geo_x = da_geo_x.values
                        else:
                            values_reshape_flip = values_reshape
                            values_geo_y = da_geo_y.values
                            values_geo_x = da_geo_x.values

                        da_var = create_darray_3d(values_reshape_flip,
                                                  datetime_idx, values_geo_x, values_geo_y,
                                                  coord_name_time=coord_name_time,
                                                  coord_name_x=coord_name_geo_x, coord_name_y=coord_name_geo_y,
                                                  dim_name_time=dim_name_time,
                                                  dim_name_x=dim_name_geo_x, dim_name_y=dim_name_geo_y,
                                                  dims_order=[dim_name_geo_y, dim_name_geo_x, dim_name_time])
                    else:
                        # da_var = da_raw
                        # values_geo_y = da_geo_y.values
                        # values_geo_x = da_geo_x.values

                        log_stream.error(' ===> Time dimension is not defined')
                        raise IOError(' ===> Case not implemented yet!')

                else:

                    values_raw = da_raw.values

                    geo_y_upper = da_geo_y.values[0, 0]
                    geo_y_lower = da_geo_y.values[-1, 0]
                    if geo_y_lower > geo_y_upper:
                        values_flip = np.flipud(values_raw)
                        values_geo_y = np.flipud(da_geo_y.values)
                        values_geo_x = da_geo_x.values
                    else:
                        values_flip = values_raw
                        values_geo_y = da_geo_y.values
                        values_geo_x = da_geo_x.values

                    if values_flip.shape.__len__() == 2:
                        values_reshape_flip = np.reshape(
                            values_flip, (values_flip.shape[0], values_flip.shape[1], 1))
                    else:
                        log_stream.error(' ===> Expected variable with 2 dimensions')
                        raise NotImplementedError(' ===> Case not implemented')

                    da_var = create_darray_3d(values_reshape_flip,
                                              datetime_idx, values_geo_x, values_geo_y,
                                              coord_name_time=coord_name_time,
                                              coord_name_x=coord_name_geo_x, coord_name_y=coord_name_geo_y,
                                              dim_name_time=dim_name_time,
                                              dim_name_x=dim_name_geo_x, dim_name_y=dim_name_geo_y,
                                              dims_order=[dim_name_geo_y, dim_name_geo_x, dim_name_time])

            if da_time is not None:
                if coord_name_time not in list(da_var.coords):
                    # da_var = da_var.squeeze(dim_name_time)
                    da_var = da_var.expand_dims({dim_name_time: datetime_idx}, axis=2)

        else:
            log_stream.warning(' ===> Dataset is None')
            da_var = None
            da_time = None
            values_geo_x = None
            values_geo_y = None
    else:
        log_stream.warning(' ===> All filenames in the selected period are not available')
        da_var = None
        da_time = None
        values_geo_x = None
        values_geo_y = None

    # Start Debug
    # mat = da_step.values
    # plt.figure()
    # plt.imshow(mat[:,:,0])
    # plt.colorbar()
    # plt.figure()
    # plt.imshow(values_geo_y)
    # plt.colorbar()
    # plt.figure()
    # plt.imshow(values_geo_x)
    # plt.colorbar()
    # plt.show()
    # End Debug

    return da_var, da_time, values_geo_x, values_geo_y
# -------------------------------------------------------------------------------------
