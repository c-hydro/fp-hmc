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
import warnings

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

            datetime_tmp = pd.date_range(start=var_time_start, end=var_time_end, freq=var_time_freq)
            datetime_idx_select = pd.DatetimeIndex(datetime_tmp)

            if os.path.exists(file_name_list[0]):
                try:

                    dst_tmp = xr.open_dataset(file_name_list[0])

                    if ('time' not in list(dst_tmp.coords)) and ('time' not in list(dst_tmp.dims)):

                        log_stream.warning(
                            ' ===> Time dimensions and coordinates are not included in filename \n "' +
                            file_name_list[0] + '". \n Time dimensions and coordinates will be assigned '
                                                'using the first step of the reference time period "' +
                            str(datetime_idx_select[0]) + '".\n')

                        datetime_idx_tmp = pd.DatetimeIndex([datetime_idx_select[0]])
                        dst_tmp['time'] = datetime_idx_tmp
                        dst_tmp = dst_tmp.set_coords('time')
                        if 'time' not in list(dst_tmp.dims):
                            dst_tmp = dst_tmp.expand_dims('time')

                    # Check the time steps of datasets and expected and in case of nan's, fill with nearest values
                    if dst_tmp['time'].__len__() > 1:
                        datetime_idx_dst_tmp = pd.DatetimeIndex(dst_tmp['time'].values)
                        datetime_idx_dst_sel = datetime_idx_dst_tmp[(datetime_idx_dst_tmp >= datetime_idx_select[0]) &
                                                                    (datetime_idx_dst_tmp <= datetime_idx_select[-1])]

                        if not datetime_idx_select.equals(datetime_idx_dst_sel):
                            if datetime_idx_select.shape[0] > datetime_idx_dst_sel.shape[0]:
                                log_stream.warning(
                                    ' ===> Datetime detection revealed a different number of time-steps between \n'
                                    'datasets (' + str(datetime_idx_dst_sel.shape[0]) + ' steps) and expected (' +
                                    str(datetime_idx_select.shape[0]) +
                                    ' steps) time-series. To avoid undefined values in the datasets time-series procedure '
                                    'automatically filled steps with nearest values. \n')

                                dst_filled = dst_tmp.reindex({"time": datetime_idx_select}, method="nearest")

                            else:
                                log_stream.warning(
                                    ' ===> Datetime detection revealed a different number of time-steps between \n'
                                    'datasets (' + str(datetime_idx_dst_sel.shape[0]) + ' steps) and expected (' +
                                    str(datetime_idx_select.shape[0]) + ' steps) time-series. Exit \n')
                                raise NotImplementedError('Case not implemented yet')

                            # Update the tmp datasets
                            dst_tmp = deepcopy(dst_filled)

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

                    # case for time_step equal to 1
                    if dst_tmp['time'].shape[0] == 1:
                        # force time coordinates and dimensions definition
                        if ('time' not in list(dst.coords)) and ('time' not in list(dst.dims)):
                            datetime_value_select = dst_tmp['time'].values
                            datetime_idx_select = pd.DatetimeIndex([datetime_value_select])
                            dst['time'] = datetime_idx_select
                            dst = dst_tmp.set_coords('time')
                            if 'time' not in list(dst.dims):
                                dst = dst.expand_dims('time')
                        elif ('time' in list(dst.coords)) and ('time' in list(dst.dims)):
                            pass
                        else:
                            log_stream.error(' ===> Time dimensions and coordinates mode is not allowed.')
                            raise NotImplementedError('Case not implemented yet')
                    elif dst_tmp['time'].shape[0] > 1:
                        pass
                    else:
                        log_stream.error(' ===> Time shape is wrongly defined')
                        raise NotImplemented('Case not implemented yet')

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
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
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

            coord_name_geo_x_select = deepcopy(coord_name_geo_x)
            if coord_name_geo_x_select not in dst_list_coords:
                coord_name_geo_x_list = ['Longitude', 'longitude', 'lon', 'Lon', 'LON']
                for coord_name_geo_x_tmp in coord_name_geo_x_list:
                    if coord_name_geo_x_tmp in dst_list_coords:
                        log_stream.warning(' ===> GeoX coord name used "' + coord_name_geo_x_select +
                                           '" but found "' + coord_name_geo_x_tmp + '" in collected datasets')
                        coord_name_geo_x_select = coord_name_geo_x_tmp
                        break

            da_geo_x = None
            if coord_name_geo_x_select in dst_list_coords:
                da_geo_x_tmp = dst[coord_name_geo_x_select]
                if dim_name_time in list(da_geo_x_tmp.dims):
                    da_geo_x = da_geo_x_tmp.squeeze(dim_name_time)
                else:
                    da_geo_x = da_geo_x_tmp
            else:
                log_stream.error(' ===> GeoX dimension name is not in the variables list of nc file')
                raise IOError(' ===> Check the GeoX dimension!')

            coord_name_geo_y_select = deepcopy(coord_name_geo_y)
            if coord_name_geo_y_select not in dst_list_coords:
                coord_name_geo_y_list = ['Latitude', 'latitude', 'lat', 'Lat', 'LAT']
                for coord_name_geo_y_tmp in coord_name_geo_y_list:
                    if coord_name_geo_y_tmp in dst_list_coords:
                        log_stream.warning(' ===> GeoY coord name used "' + coord_name_geo_y_select +
                                           '" but found "' + coord_name_geo_y_tmp + '" in collected datasets')
                        coord_name_geo_y_select = coord_name_geo_y_tmp
                        break

            da_geo_y = None
            if coord_name_geo_y_select in dst_list_coords:
                da_geo_y_tmp = dst[coord_name_geo_y_select]
                if dim_name_time in list(da_geo_y_tmp.dims):
                    da_geo_y = da_geo_y_tmp.squeeze(dim_name_time)
                else:
                    da_geo_y = da_geo_y_tmp
            else:
                log_stream.error(' ===> GeoY dimension name is not in the variables list of nc file')
                raise IOError(' ===> Check the GeoY dimension!')

            # Check dimensions not allowed in the datasets (for example: "height")
            dst_list_coords_expected = [coord_name_geo_x_select, coord_name_geo_y_select, coord_name_time]
            dst_list_coords_tmp = deepcopy(dst_list_coords)
            for coord_name in dst_list_coords_expected:
                if coord_name in dst_list_coords:
                    dst_list_coords_tmp.remove(coord_name)
            if dst_list_coords_tmp.__len__() > 0:
                log_stream.warning(' ===> Datasets coordinates "' + ','.join(dst_list_coords_tmp) + '" are not allowed')
                dst_tmp = deepcopy(dst)
                for coord_name_tmp in dst_list_coords_tmp:
                    log_stream.warning(' ===> Coordinate "' + coord_name_tmp + '" is not expected in dataset')
                    if dst_tmp.coords[coord_name_tmp].shape[0] == 1:
                        log_stream.warning(' ===> Coordinate "' + coord_name_tmp +
                                           '" dimension equal to 1. Try to correct the dataset')
                        dst_tmp = dst_tmp.squeeze(coord_name_tmp)
                        dst_tmp = dst_tmp.drop(coord_name_tmp)
                        dst_tmp_list_coords = list(dst_tmp.coords)
                    else:
                        log_stream.error(' ===> Coordinate "' + coord_name_tmp +
                                         '" dimension greater than 1. Dataset cannot be correct ')
                        raise NotImplementedError('Case not implemented yet')
                dst = deepcopy(dst_tmp)
                dst_list_coords = deepcopy(dst_tmp_list_coords)
                log_stream.warning(' ===> Datasets coordinates were corrected but errors could be found')

            # Check the dimensions of GeoX and GeoY
            if (da_geo_x is not None) and (da_geo_y is not None):

                values_geo_x_tmp = da_geo_x.values
                values_geo_y_tmp = da_geo_y.values

                if (values_geo_x_tmp.shape.__len__() == 1) and (values_geo_y_tmp.shape.__len__() == 1):
                    log_stream.warning(' ===> GeoX and GeoY are in 1D format. Meshgrid will be applied to define 2D')
                    values_geo_x_def, values_geo_y_def = np.meshgrid(values_geo_x_tmp, values_geo_y_tmp)
                elif (values_geo_x_tmp.shape.__len__() == 2) and (values_geo_y_tmp.shape.__len__() == 2):
                    values_geo_x_def = values_geo_x_tmp
                    values_geo_y_def = values_geo_y_tmp
                else:
                    log_stream.error(' ===> GeoX and GeoY are available but in a unsupported format')
                    raise NotImplemented(' ===> GeoX and GeoY format not implemented yet')
            else:
                log_stream.error(' ===> GeoX or GeoY datasets are unavailable')
                raise IOError(' ===> GeoX and GeoY datasets must be in the data workspace')

            if da_time is not None:
                time_stamp_period = []

                if da_time.values.size == 1:
                    time_list = [da_time.values]
                elif da_time.values.size > 1:
                    time_list = da_time.values
                else:
                    log_stream.error(' ===> Time values are not greater than 0')
                    raise NotImplemented(' ===> Case not implemented yet')

                for time_step in time_list:
                    timestamp_step = pd.to_datetime(time_step, format='%Y-%m-%d_%H:%M:%S')
                    timestamp_step = timestamp_step.round('H')
                    time_stamp_period.append(timestamp_step)
                datetime_idx = pd.DatetimeIndex(time_stamp_period)
            else:
                datetime_idx = None

            if var_name == 'ALL':

                geo_y_upper = values_geo_y_def[0, 0]
                geo_y_lower = values_geo_y_def[-1, 0]
                if geo_y_lower > geo_y_upper:
                    values_geo_y = np.flipud(values_geo_y_def)
                    values_geo_x = values_geo_x_def

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

                    values_geo_y = values_geo_y_def
                    values_geo_x = values_geo_x_def
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

                        geo_y_upper = values_geo_y_def[0, 0]
                        geo_y_lower = values_geo_y_def[-1, 0]
                        if geo_y_lower > geo_y_upper:
                            values_reshape_flip = np.flipud(values_reshape)
                            values_geo_y = np.flipud(values_geo_y_def)
                            values_geo_x = values_geo_x_def
                        else:
                            values_reshape_flip = values_reshape
                            values_geo_y = values_geo_y_def
                            values_geo_x = values_geo_x_def

                        da_var = create_darray_3d(values_reshape_flip,
                                                  datetime_idx, values_geo_x, values_geo_y,
                                                  coord_name_time=coord_name_time,
                                                  coord_name_x=coord_name_geo_x, coord_name_y=coord_name_geo_y,
                                                  dim_name_time=dim_name_time,
                                                  dim_name_x=dim_name_geo_x, dim_name_y=dim_name_geo_y,
                                                  dims_order=[dim_name_geo_y, dim_name_geo_x, dim_name_time])
                    else:
                        # da_var = da_raw
                        # values_geo_y = values_geo_y_def
                        # values_geo_x = values_geo_x_def

                        log_stream.error(' ===> Time dimension is not defined')
                        raise IOError(' ===> Case not implemented yet!')

                else:

                    values_raw = da_raw.values

                    geo_y_upper = values_geo_y_def[0, 0]
                    geo_y_lower = values_geo_y_def[-1, 0]
                    if geo_y_lower > geo_y_upper:
                        values_flip = np.flipud(values_raw)
                        values_geo_y = np.flipud(values_geo_y_def)
                        values_geo_x = values_geo_x_def
                    else:
                        values_flip = values_raw
                        values_geo_y = values_geo_y_def
                        values_geo_x = values_geo_x_def

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
