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

from tools.processing_tool_datasets_merger.lib_info_args import logger_name

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
def read_data_nc(file_name, geo_ref_x=None, geo_ref_y=None, geo_ref_attrs=None, geo_no_data=-9999.0,
                 var_coords=None, var_scale_factor=1, var_name=None, var_time=None, var_no_data=-9999.0,
                 coord_name_time='time', coord_name_geo_x='Longitude', coord_name_geo_y='Latitude',
                 dim_name_time='time', dim_name_geo_x='west_east', dim_name_geo_y='south_north',
                 dims_order=None, decimal_round=4):

    if var_coords is None:
        var_coords = {'x': 'Longitude', 'y': 'Latitude', 'time': 'time'}

    if dims_order is None:
        dims_order = [dim_name_geo_y, dim_name_geo_x, dim_name_time]

    if not isinstance(var_name, list):
        var_name = [var_name]
    if not isinstance(var_scale_factor, list):
        var_scale_factor = [var_scale_factor]
    if not isinstance(var_no_data, list):
        var_no_data = [var_no_data]
    if var_name.__len__() != var_scale_factor.__len__():
        log_stream.error(' ===> Variable name(s) and scale factor(s) must have the same dimension.')
        raise RuntimeError('Check your setting file and define the variable using the same length of object.')
    if var_name.__len__() != var_no_data.__len__():
        log_stream.error(' ===> Variable name(s) and no data value(s) must have the same dimension.')
        raise RuntimeError('Check your setting file and define the variable using the same length of object.')

    data_workspace, file_attrs = None, None
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

        for var_name_step, var_scale_factor_step, var_no_data_step in zip(var_name, var_scale_factor, var_no_data):

            if data_workspace is None:
                data_workspace = {}
            data_workspace[var_name_step] = {}

            if var_name_step in file_variables:

                var_data = file_handle[var_name_step].values
                var_data = np.float32(var_data / var_scale_factor_step)
                var_data[var_data == var_no_data_step] = np.nan

                '''
                # DEBUG
                import matplotlib.pylab as plt
                plt.figure()
                plt.imshow(var_data)
                plt.colorbar()
                plt.show()
                '''

                if 'time' in list(idx_coords.keys()):
                    if idx_coords['time'] is not None:
                        coord_name_time = file_coords[idx_coords['time']]
                        if file_handle[coord_name_time].size == 1:
                            if var_data.shape.__len__() < file_coords.__len__():
                                var_data = var_data[:, :, np.newaxis]
                            elif var_data.shape.__len__() == file_coords.__len__():
                                pass
                            else:
                                log_stream.error(' ===> File shape is greater than expected coords')
                                raise NotImplemented('Case not implemented yet')
                        else:
                            log_stream.error(' ===> Coordinate "time" is defined by size greater than 1')
                            raise NotImplemented('Case not implemented yet')
                    else:
                        if var_data.ndim > 2:
                            log_stream.error(' ===> Coordinate "time" is defined by NoneType with data length > 1')
                            raise IOError('Coordinate "time" is not available')

                geo_data_x = None
                geo_ref_x_2d, geo_ref_y_2d = np.meshgrid(geo_ref_x, geo_ref_y)
                for step_coords_x in ['x', 'X']:
                    if step_coords_x in idx_coords:
                        coord_name_x = file_coords[idx_coords[step_coords_x]]
                        geo_data_x = file_handle[coord_name_x].values
                        break
                if geo_data_x is None:
                    log_stream.error(' ===> Coordinate "geo_data_x" is defined by NoneType')
                    raise IOError('Coordinate "geo_data_x" is not available or not defined')

                geo_data_y = None
                for step_coords_y in ['y', 'Y']:
                    if step_coords_y in idx_coords:
                        coord_name_y = file_coords[idx_coords[step_coords_y]]
                        geo_data_y = file_handle[coord_name_y].values
                        break
                if geo_data_y is None:
                    log_stream.error(' ===> Coordinate "geo_data_y" is defined by NoneType')
                    raise IOError('Coordinate "geo_data_y" is not available or not defined')

                # Check if geo_x 2d array is not defined everywhere
                if (geo_data_x == geo_no_data).any():
                    log_stream.warning(
                        ' ===> Variable(s) "geo_data_x" is not defined everywhere \n'
                        'but probably is masked using the dem extension. The value of "geo_data_x" must be \n'
                        'defined everywhere and for skipping this issue the "geo_x_ref" will be used.')
                    geo_data_x = deepcopy(geo_ref_x_2d)

                # Check if geo_y 2d array is not defined everywhere
                if (geo_data_y == geo_no_data).any():

                    geo_y_array = geo_data_y.max(axis=1)
                    geo_y_array[geo_y_array == -9999] = np.nan
                    geo_y_array = geo_y_array[~np.isnan(geo_y_array)]

                    geo_y_upper_grid_file, geo_y_lower_grid_file = geo_y_array[0], geo_y_array[-1]
                    geo_y_upper_grid_ref, geo_y_lower_grid_ref = geo_ref_y_2d[0, 0], geo_ref_y_2d[-1, 0]

                    log_stream.warning(
                        ' ===> Variable(s) "geo_data_y" is not defined everywhere \n'
                        'but probably is masked using the dem extension. The value of "geo_data_y" must be \n'
                        'defined everywhere and for skipping this issue the "geo_y_ref" will be used.')

                    geo_data_y = deepcopy(geo_ref_y_2d)

                    if geo_y_lower_grid_file > geo_y_upper_grid_file:
                        var_data = np.flipud(var_data)
                    if geo_y_lower_grid_ref > geo_y_upper_grid_ref:
                        geo_data_y = np.flipud(geo_data_y)

                else:

                    geo_y_upper, geo_y_lower = geo_data_y[0, 0], geo_data_y[-1, 0]
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

                    # Check geo x rounding
                    if geo_check_x[0, 0] != 0:
                        if np.float32(round(geo_check_x[0, 0], decimal_round)) == 0:
                            log_stream.error(' ===> Variable "geo_check_x_start" was rounded to zero')
                            raise RuntimeError('The used "decimal round" is not suitable for the grid resolution')
                    if geo_check_x[1, -1] != 0:
                        if np.float32(round(geo_check_x[1, -1], decimal_round)) == 0:
                            log_stream.error(' ===> Variable "geo_check_x_end" was rounded to zero')
                            raise RuntimeError('The used "decimal round" is not suitable for the grid resolution')
                    if geo_data_x[0, 0] != 0:
                        if np.float32(round(geo_data_x[0, 0], decimal_round)) == 0:
                            log_stream.error(' ===> Variable "geo_data_x_start" was rounded to zero')
                            raise RuntimeError('The used "decimal round" is not suitable for the grid resolution')
                    if geo_data_x[1, -1] != 0:
                        if np.float32(round(geo_data_x[1, -1], decimal_round)) == 0:
                            log_stream.error(' ===> Variable "geo_data_x_end" was rounded to zero')
                            raise RuntimeError('The used "decimal round" is not suitable for the grid resolution')
                    # Check geo y rounding
                    if geo_check_y[0, 0] != 0:
                        if np.float32(round(geo_check_y[0, 0], decimal_round)) == 0:
                            log_stream.error(' ===> Variable "geo_check_y_start" was rounded to zero')
                            raise RuntimeError('The used "decimal round" is not suitable for the grid resolution')
                    if geo_check_y[1, -1] != 0:
                        if np.float32(round(geo_check_y[1, -1], decimal_round)) == 0:
                            log_stream.error(' ===> Variable "geo_check_y_end" was rounded to zero')
                            raise RuntimeError('The used "decimal round" is not suitable for the grid resolution')
                    if geo_data_y[0, 0] != 0:
                        if np.float32(round(geo_data_y[0, 0], decimal_round)) == 0:
                            log_stream.error(' ===> Variable "geo_data_y_start" was rounded to zero')
                            raise RuntimeError('The used "decimal round" is not suitable for the grid resolution')
                    if geo_data_y[1, -1] != 0:
                        if np.float32(round(geo_data_y[1, -1], decimal_round)) == 0:
                            log_stream.error(' ===> Variable "geo_data_y_end" was rounded to zero')
                            raise RuntimeError('The used "decimal round" is not suitable for the grid resolution')

                    # Check geo grid(s)
                    geo_cellsize = np.float32(round(geo_ref_attrs['cellsize'], decimal_round) / 2)
                    if (not geo_check_start_x == geo_data_start_x) or (not geo_check_end_x == geo_data_end_x):
                        geo_diff_start_x = np.float32(
                            round(np.abs(geo_check_x[0, 0] - geo_data_x[0, 0]), decimal_round))
                        geo_diff_end_x = np.float32(
                            round(np.abs(geo_check_x[-1, -1] - geo_data_x[-1, -1]), decimal_round))
                        log_stream.warning(
                            ' ===> Variable "geo x start" or/and "geo x end" is/are not the same; try to correct using '
                            'the reference "cellsize" to correct the "geo x grid" ')

                        assert geo_diff_start_x == geo_cellsize, \
                            ' ===> Variable "geo x start" is not verified by the "cellsize"'
                        assert geo_diff_end_x == geo_cellsize, \
                            ' ===> Variable "geo x end" is not verified by the "cellsize"'

                        geo_data_x = deepcopy(geo_check_x)
                        geo_data_start_x = np.float32(round(geo_data_x[0, 0], decimal_round))
                        geo_data_end_x = np.float32(round(geo_data_x[-1, -1], decimal_round))

                        log_stream.warning(
                            ' ===> Variable "geo x grid" is corrected by the reference grid by checking the difference'
                            'in terms of the "cellsize"; the grids have a difference at maximum of "cellsize / 2"')

                    if (not geo_check_start_y == geo_data_start_y) or (not geo_check_end_y == geo_data_end_y):
                        geo_diff_start_y = np.float32(
                            round(np.abs(geo_check_y[0, 0] - geo_data_y[0, 0]), decimal_round))
                        geo_diff_end_y = np.float32(
                            round(np.abs(geo_check_y[-1, -1] - geo_data_y[-1, -1]), decimal_round))
                        log_stream.warning(
                            ' ===> Variable "geo y start" or/and "geo y end" is/are not the same; try to correct using '
                            'the reference "cellsize" to correct the "geo y grid" ')

                        assert geo_diff_start_y == geo_cellsize, \
                            ' ===> Variable "geo y start" is not verified by the "cellsize"'
                        assert geo_diff_end_y == geo_cellsize, \
                            ' ===> Variable "geo y end" is not verified by the "cellsize"'

                        geo_data_y = deepcopy(geo_check_y)
                        geo_data_start_y = np.float32(round(geo_data_y[0, 0], decimal_round))
                        geo_data_end_y = np.float32(round(geo_data_y[-1, -1], decimal_round))

                        log_stream.warning(
                            ' ===> Variable "geo y grid" is corrected by the reference grid by checking the difference'
                            'in terms of the "cellsize"; the grids have a difference at maximum of "cellsize / 2"')

                    assert geo_check_start_x == geo_data_start_x, ' ===> Variable geo x start != Reference geo x start'
                    assert geo_check_start_y == geo_data_start_y, ' ===> Variable geo y start != Reference geo y start'
                    assert geo_check_end_x == geo_data_end_x, ' ===> Variable geo x end != Reference geo x end'
                    assert geo_check_end_y == geo_data_end_y, ' ===> Variable geo y end != Reference geo y end'
                else:
                    log_stream.warning(' ===> GeoX and GeoY variables have not compared with a reference GeoX and GeoY')

                data_workspace[var_name_step] = var_data

            else:
                log_stream.warning(' ===> Variable ' + var_name_step + ' not available in loaded datasets!')
                data_workspace[var_name_step] = None

    else:
        log_stream.warning(' ===> File ' + file_name + ' not available in loaded datasets!')

    if data_workspace is not None:

        if var_time is not None:

            if isinstance(var_time, pd.Timestamp):
                var_data_time = pd.DatetimeIndex([var_time])
            elif isinstance(var_time, pd.DatetimeIndex):
                var_data_time = deepcopy(var_time)
            else:
                log_stream.error(' ===> Time format is not allowed. Expected Timestamp or Datetimeindex')
                raise NotImplemented('Case not implemented yet')

            var_dset = xr.Dataset(coords={coord_name_time: ([dim_name_time], var_data_time)})
            var_dset.coords[coord_name_time] = var_dset.coords[coord_name_time].astype('datetime64[ns]')

            for var_name, var_data in data_workspace.items():
                if var_data is not None:
                    var_da = xr.DataArray(var_data, name=var_name, dims=dims_order,
                                          coords={coord_name_time: ([dim_name_time], var_data_time),
                                                  coord_name_geo_x: ([dim_name_geo_x], geo_data_x[0, :]),
                                                  coord_name_geo_y: ([dim_name_geo_y], geo_data_y[:, 0])})
                    var_dset[var_name] = var_da

        elif var_time is None:

            var_dset = xr.Dataset()
            for var_name, var_data in data_workspace.items():
                if var_data is not None:
                    var_da = xr.DataArray(var_data, name=var_name, dims=dims_order,
                                          coords={coord_name_geo_x: ([dim_name_geo_x], geo_data_x[0, :]),
                                                  coord_name_geo_y: ([dim_name_geo_y], geo_data_y[:, 0])})
                    var_dset[var_name] = var_da

        else:
            log_stream.error(' ===> Error in creating time information for dataset object')
            raise RuntimeError('Unknown error in creating dataset. Check the procedure.')

        if file_attrs and geo_ref_attrs:
            dset_attrs = {**file_attrs, **geo_ref_attrs}
        elif (not file_attrs) and geo_ref_attrs:
            dset_attrs = deepcopy(geo_ref_attrs)
        elif file_attrs and (not geo_ref_attrs):
            dset_attrs = deepcopy(file_attrs)
        else:
            dset_attrs = None

        if dset_attrs is not None:
            var_dset.attrs = dset_attrs

    else:
        log_stream.warning(' ===> All filenames in the selected period are not available')
        var_dset = None

    return var_dset

# -------------------------------------------------------------------------------------
