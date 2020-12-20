"""
Library Features:

Name:          lib_data_io_generic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#################################################################################

# -------------------------------------------------------------------------------
# Libraries
import logging
import os
import pickle
import json
import glob

import pandas as pd
import xarray as xr
import numpy as np

from copy import deepcopy

from hmc.algorithm.utils.lib_utils_geo import clip_map

from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Attr(s) decoded
attrs_reserved = ['coordinates']
attrs_decoded = ['_FillValue', 'scale_factor']
attr_valid_range = 'Valid_range'
attr_missing_value = 'Missing_value'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to swap da dimensions
def swap_darray_dims(da_ref, da_tmp, da_terrain, da_excluded_dims=None):

    if da_excluded_dims is None:
        da_excluded_dims = ['time']

    dims_ref = list(da_ref.dims)
    dims_tmp = list(da_tmp.dims)
    dims_terrain = list(da_terrain.dims)

    shape_ref = da_ref.shape
    shape_tmp = da_tmp.shape
    shape_terrain = da_terrain.shape

    for excluded_dim in da_excluded_dims:
        if excluded_dim in dims_ref:
            idx_ref = dims_ref.index(excluded_dim)
            shape_list = list(shape_ref)
            shape_list.pop(idx_ref)
            shape_ref = tuple(shape_list)
            dims_ref.remove(excluded_dim)
        if excluded_dim in dims_tmp:
            idx_tmp = dims_tmp.index(excluded_dim)
            shape_list = list(shape_tmp)
            shape_list.pop(idx_tmp)
            shape_tmp = tuple(shape_list)
            dims_tmp.remove(excluded_dim)

    if dims_ref.__len__() < dims_tmp.__len__():
        dims_tmp_select = []
        shape_tmp_select = []
        for dim_tmp, value_tmp in zip(dims_tmp, shape_tmp):
            if dim_tmp in dims_ref:
                dims_tmp_select.append(dim_tmp)
                shape_tmp_select.append(value_tmp)
        shape_tmp_select = tuple(shape_tmp_select)
    else:
        dims_tmp_select = dims_tmp
        shape_tmp_select = shape_tmp

    swap_dict = {}
    if dims_ref != dims_tmp_select:
        for dim_terrain, value_terrain in zip(dims_terrain, shape_terrain):

            idx_terrain_dim = dims_terrain.index(dim_terrain)
            idx_tmp_dim = dims_tmp_select.index(dim_terrain)
            idx_ref_dim = dims_ref.index(dim_terrain)

            if (idx_ref_dim == idx_terrain_dim) and (idx_tmp_dim != idx_terrain_dim):

                name_tmp_dim = dims_tmp_select[idx_terrain_dim]
                name_terrain_dim = dims_terrain[idx_terrain_dim]

                value_tmp = shape_tmp_select[idx_terrain_dim]
                value_ref = shape_ref[idx_terrain_dim]

                if (value_tmp == value_terrain) and (value_ref == value_terrain):
                    swap_dict[name_tmp_dim] = name_terrain_dim
                else:
                    log_stream.error(' ===> Swapping dimensions is not possible because values are different')
                    raise IOError('Mismatching in data dimensions')
            else:
                log_stream.error(' ===> Swapping dimensions case is not correctly defined')
                raise NotImplemented('Case is not implemented yet')

        da_def = da_tmp.rename(swap_dict)

    else:
        da_def = da_tmp

    return da_def
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to reshape 3d variable
def reshape_var3d(var_values_in):
    var_shape = var_values_in.shape
    var_values_out = np.zeros([var_shape[1], var_shape[2], var_shape[0]])
    for id_step, var_step in enumerate(var_values_in):
        var_value_step = var_values_in[id_step, :, :]
        var_values_out[:, :, id_step] = var_value_step
    return var_values_out
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a data array
def create_darray_2d(data, geo_x, geo_y, geo_1d=True, time=None,
                     coord_name_x='west_east', coord_name_y='south_north', coord_name_time='time',
                     dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                     dims_order=None):

    if dims_order is None:
        dims_order = [dim_name_y, dim_name_x]
    if time is not None:
        dims_order = [dim_name_y, dim_name_x, dim_name_time]

    if geo_1d:
        if geo_x.shape.__len__() == 2:
            geo_x = geo_x[0, :]
        if geo_y.shape.__len__() == 2:
            geo_y = geo_y[:, 0]

        if time is None:
            data_da = xr.DataArray(data,
                                   dims=dims_order,
                                   coords={coord_name_x: (dim_name_x, geo_x),
                                           coord_name_y: (dim_name_y, geo_y)})
        elif isinstance(time, pd.DatetimeIndex):

            if data.shape.__len__() == 2:
                data = np.expand_dims(data, axis=-1)

            data_da = xr.DataArray(data,
                                   dims=dims_order,
                                   coords={coord_name_x: (dim_name_x, geo_x),
                                           coord_name_y: (dim_name_y, geo_y),
                                           coord_name_time: (dim_name_time, time)})
        else:
            log_stream.error(' ===> Time obj is in wrong format')
            raise IOError('Variable time format not valid')

    else:
        log_stream.error(' ===> Longitude and Latitude must be 1d')
        raise IOError('Variable shape is not valid')

    return data_da
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a data array
def create_darray_3d(data, time, geo_x, geo_y, geo_1d=True,
                     coord_name_x='west_east', coord_name_y='south_north', coord_name_time='time',
                     dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                     dims_order=None):

    if dims_order is None:
        dims_order = [dim_name_y, dim_name_x, dim_name_time]

    if geo_1d:
        if geo_x.shape.__len__() == 2:
            geo_x = geo_x[0, :]
        if geo_y.shape.__len__() == 2:
            geo_y = geo_y[:, 0]

        data_da = xr.DataArray(data,
                               dims=dims_order,
                               coords={coord_name_time: (dim_name_time, time),
                                       coord_name_x: (dim_name_x, geo_x),
                                       coord_name_y: (dim_name_y, geo_y)})
    else:
        log_stream.error(' ===> Longitude and Latitude must be 1d')
        raise IOError('Variable shape is not valid')

    return data_da
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to select attributes
def select_attrs(var_attrs_raw):

    var_attrs_select = {}
    if var_attrs_raw:
        for var_key, var_value in var_attrs_raw.items():
            if var_value is not None:
                if var_key not in attrs_decoded:
                    if isinstance(var_value, list):
                        var_string = [str(value) for value in var_value]
                        var_value = ','.join(var_string)
                    if isinstance(var_value, dict):
                        var_string = json.dumps(var_value)
                        var_value = var_string
                    if var_key in attrs_reserved:
                        var_value = None
                    if var_value is not None:
                        var_attrs_select[var_key] = var_value

    return var_attrs_select
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create dataset
def create_dset(var_data_values,
                var_geo_values, var_geo_x, var_geo_y,
                var_data_time=None,
                var_data_name='variable', var_geo_name='terrain', var_data_attrs=None, var_geo_attrs=None,
                var_geo_1d=False,
                file_attributes=None,
                coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
                dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                dims_order_2d=None, dims_order_3d=None):

    var_geo_x_tmp = var_geo_x
    var_geo_y_tmp = var_geo_y
    if var_geo_1d:
        if (var_geo_x.shape.__len__() == 2) and (var_geo_y.shape.__len__() == 2):
            var_geo_x_tmp = var_geo_x[0, :]
            var_geo_y_tmp = var_geo_y[:, 0]
    else:
        if (var_geo_x.shape.__len__() == 1) and (var_geo_y.shape.__len__() == 1):
            var_geo_x_tmp, var_geo_y_tmp = np.meshgrid(var_geo_x, var_geo_y)

    if dims_order_2d is None:
        dims_order_2d = [dim_name_y, dim_name_x]
    if dims_order_3d is None:
        dims_order_3d = [dim_name_y, dim_name_x, dim_name_time]

    var_dset = xr.Dataset(coords={coord_name_time: ([dim_name_time], var_data_time)})
    var_dset.coords[coord_name_time] = var_dset.coords[coord_name_time].astype('datetime64[ns]')

    if file_attributes:
        if isinstance(file_attributes, dict):
            var_dset.attrs = file_attributes

    var_da_terrain = xr.DataArray(np.flipud(var_geo_values),  name=var_geo_name,
                                  dims=dims_order_2d,
                                  coords={coord_name_x: ([dim_name_y, dim_name_x], var_geo_x_tmp),
                                          coord_name_y: ([dim_name_y, dim_name_x], np.flipud(var_geo_y_tmp))})
    var_dset[var_geo_name] = var_da_terrain
    var_geo_attrs_select = select_attrs(var_geo_attrs)

    if var_geo_attrs_select is not None:
        var_dset[var_geo_name].attrs = var_geo_attrs_select

    if var_data_values.shape.__len__() == 2:
        var_da_data = xr.DataArray(np.flipud(var_data_values), name=var_data_name,
                                   dims=dims_order_2d,
                                   coords={coord_name_x: ([dim_name_y, dim_name_x], var_geo_x_tmp),
                                           coord_name_y: ([dim_name_y, dim_name_x], np.flipud(var_geo_y_tmp))})
    elif var_data_values.shape.__len__() == 3:
        var_da_data = xr.DataArray(np.flipud(var_data_values), name=var_data_name,
                                   dims=dims_order_3d,
                                   coords={coord_name_time: ([dim_name_time], var_data_time),
                                           coord_name_x: ([dim_name_y, dim_name_x], var_geo_x_tmp),
                                           coord_name_y: ([dim_name_y, dim_name_x], np.flipud(var_geo_y_tmp))})
    else:
        raise NotImplemented

    if var_data_attrs is not None:
        if attr_valid_range in list(var_data_attrs.keys()):
            valid_range = var_data_attrs[attr_valid_range]
            var_da_data = clip_map(var_da_data, valid_range)

        if attr_missing_value in list(var_data_attrs.keys()):
            missing_value = var_data_attrs[attr_missing_value]
            var_da_data = var_da_data.where(var_da_terrain > 0, other=missing_value)

    var_dset[var_data_name] = var_da_data
    if var_data_attrs is not None:
        var_data_attrs_select = select_attrs(var_data_attrs)
    else:
        var_data_attrs_select = None

    if var_data_attrs_select is not None:
        var_dset[var_data_name].attrs = var_data_attrs_select

    return var_dset

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write dataset
def write_dset(file_name,
               dset_data, dset_attrs=None,
               dset_mode='w', dset_engine='h5netcdf', dset_compression=0, dset_format='NETCDF4',
               dim_key_time='time', fill_data=-9999.0):

    dset_encoded = dict(zlib=True, complevel=dset_compression, _FillValue=fill_data)

    dset_encoding = {}
    for var_name in dset_data.data_vars:

        if isinstance(var_name, bytes):
            var_name_upd = var_name.decode("utf-8")
            dset_data = var_name.rename({var_name: var_name_upd})
            var_name = var_name_upd

        var_data = dset_data[var_name]
        var_attrs = dset_data[var_name].attrs
        if len(var_data.dims) > 0:
            dset_encoding[var_name] = deepcopy(dset_encoded)

        if var_attrs:
            for attr_key, attr_value in var_attrs.items():
                if attr_key in attrs_decoded:

                    dset_encoding[var_name][attr_key] = {}

                    if isinstance(attr_value, list):
                        attr_string = [str(value) for value in attr_value]
                        attr_value = ','.join(attr_string)

                    dset_encoding[var_name][attr_key] = attr_value

            if '_FillValue' not in list(dset_encoding[var_name].keys()):
                dset_encoding[var_name]['_FillValue'] = fill_data

    if dim_key_time in list(dset_data.coords):
        dset_encoding[dim_key_time] = {'calendar': 'gregorian'}

    dset_data.to_netcdf(path=file_name, format=dset_format, mode=dset_mode, engine=dset_engine,
                        encoding=dset_encoding)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to store file
def store_file(file_name, file_ext='.old.{}', file_max=1):

    # Get file folder
    file_folder = os.path.split(file_name)[0]

    # Iterate to store old logging file
    if os.path.exists(file_name):

        file_loop = file_name
        file_id = 0
        while os.path.exists(file_loop):
            file_id = file_id + 1
            file_loop = file_name + file_ext.format(file_id)

            if file_id > file_max:
                file_obj = glob.glob(os.path.join(file_folder, '*'))
                for file_step in file_obj:
                    if file_step.startswith(file_name):
                        os.remove(file_step)
                file_loop = file_name
                break

        if file_loop:
            if file_name != file_loop:
                os.rename(file_name, file_loop)

    return file_loop
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data obj
def read_obj(filename):
    if os.path.exists(filename):
        data = pickle.load(open(filename, "rb"))
    else:
        data = None
    return data
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write data obj
def write_obj(filename, data):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
# -------------------------------------------------------------------------------------



