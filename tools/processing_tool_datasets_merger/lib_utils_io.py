"""
Library Features:

Name:          lib_utils_io
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Libraries
import logging

import os
import pickle
import tempfile

import rasterio as rio
import pandas as pd
import xarray as xr
import numpy as np

from copy import deepcopy

from tools.processing_tool_datasets_merger.lib_info_args import logger_name
from tools.processing_tool_datasets_merger.lib_data_io_tiff import write_data_tiff

# Logging
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

# Defined attributes look-up table
attributes_defined_lut = {
    'blocking_attrs': ['coordinates'],
    'encoding_attrs': {
        '_FillValue': ['_FillValue', 'fill_value'],
        'scale_factor': ['scale_factor', 'ScaleFactor']
    },
    'filtering_attrs': {
        'Valid_range': ['Valid_range', 'valid_range'],
        'Missing_value': ['Missing_value', 'missing_value']
    }
}
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a data array
def create_darray_2d(data, geo_x, geo_y, geo_1d=True, time=None, name=None,
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

    if name is not None:
        data_da.name = name

    return data_da
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a data array
def create_darray_3d(data, time, geo_x, geo_y, geo_1d=True, var_name=None,
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
                               name=var_name,
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
# Method to adjust dataset variable(s)
def adjust_dset_vars(var_dset_1_default, var_dset_2_default):

    if not isinstance(var_dset_1_default, xr.Dataset):
        log_stream.error(' ===> Variable obj must be a Dataset')
    if not isinstance(var_dset_2_default, xr.Dataset):
        log_stream.error(' ===> Variable obj must be a Dataset')

    var_name_list_1 = list(var_dset_1_default.variables)
    var_name_list_2 = list(var_dset_2_default.variables)

    if set(var_name_list_1) != set(var_name_list_2):
        var_name_list_common = []
        for var_name_step_2 in var_name_list_2:
            if var_name_step_2 in var_name_list_1:
                var_name_list_common.append(var_name_step_2)
            else:
                log_stream.warning(' ===> Variable name "' + var_name_step_2
                                   + '" is not included in the reference dataset. Variable will be removed.')

        var_dset_1_common = var_dset_1_default[var_name_list_common]
        var_dset_2_common = var_dset_2_default[var_name_list_common]
    else:
        var_dset_1_common = deepcopy(var_dset_1_default)
        var_dset_2_common = deepcopy(var_dset_2_default)

    return var_dset_1_common, var_dset_2_common
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to filter dataset
def filter_dset_vars(var_dset, var_list=None):

    if not isinstance(var_dset, xr.Dataset):
        log_stream.error(' ===> Variable obj must be a Dataset')

    if var_list is not None:
        if not isinstance(var_list, list):
            var_list = [var_list]
        var_list_tmp, var_list_filter = deepcopy(var_list), []
        for var_step in var_list_tmp:
            if var_step in list(var_dset.variables):
                var_list_filter.append(var_step)
            else:
                log_stream.warning(' ===> Filter name "' + var_step +
                                   '" is not included in the datasets. Check the name in the settings file.')
        var_dset_filtered = var_dset[var_list_filter]
    else:
        var_dset_filtered = deepcopy(var_dset)

    return var_dset_filtered
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to save datasets in tiff format
def write_dset_tiff(file_name_dict, file_dset, file_compression_option=None, file_epsg_code='EPSG:4326',
                    geo_x_dim='longitude', geo_y_dim='latitude', time_dim='time'):

    file_data_dict = {}
    file_data_height, file_data_width, file_geo_x, file_geo_y, file_time = None, None, None, None, None
    for file_var in list(file_dset.variables):
        if file_var not in [geo_x_dim, geo_y_dim, time_dim]:
            file_data = file_dset[file_var].values

            if file_data.ndim == 3:
                if file_data.shape[2] == 1:
                    file_data = np.squeeze(file_data, axis=2)
                else:
                    log_stream.error(' ===> Only datasets with 1 time step are allowed')
                    raise NotImplemented('Case not implemented yet')
            elif file_data.ndim == 2:
                pass
            else:
                log_stream.error(' ===> Datasets dimensions must be 2D or 3D')
                raise NotImplemented('Case not implemented yet')

            if (file_data_height is None) or (file_data_width is None):
                file_data_height, file_data_width = file_data.shape

            file_data_dict[file_var] = file_data

        elif file_var == geo_x_dim:
            file_data = file_dset[file_var].values
            file_geo_x = deepcopy(file_data)
        elif file_var == geo_y_dim:
            file_data = file_dset[file_var].values
            file_geo_y = deepcopy(file_data)
        elif file_var == time_dim:
            file_data = file_dset[file_var].values
            file_time = deepcopy(file_data)

    if (file_geo_x is not None) and (file_geo_y is not None):
        file_geo_x_west = np.min(file_geo_x)
        file_geo_x_east = np.max(file_geo_x)
        file_geo_y_south = np.min(file_geo_y)
        file_geo_y_north = np.max(file_geo_y)

        file_data_transform = rio.transform.from_bounds(
            file_geo_x_west, file_geo_y_south, file_geo_x_east, file_geo_y_north,
            file_data_width, file_data_height)
    else:
        log_stream.error(' ===> GeoX and GeoY datasets are not defined.')
        raise RuntimeError('Geographical information must be defined to save the file(s)')

    if set(list(file_name_dict.values())) == 1:

        file_name_list = list(set(list(file_name_dict.values())))

        file_data_list, file_metadata_list = [], []
        for var_name, var_data in file_data_dict.items():
            file_data_list.append(var_data)
            file_metadata_list.append({'description_field': var_name})

        write_data_tiff(file_name_list, file_data_list,
                        file_data_width, file_data_height, file_data_transform, file_epsg_code,
                        file_metadata=file_metadata_list, file_compression=file_compression_option)
    else:
        file_data_list, file_name_list, file_metadata_list = [], [], []
        for var_id, (var_name, file_data_step) in enumerate(file_data_dict.items()):

            if var_name in list(file_name_dict.keys()):
                file_name_step = file_name_dict[var_name]
            else:
                file_name_step = None

            if file_name_step is not None:
                file_data_list.append(file_data_step)
                file_name_list.append(file_name_step)
                file_metadata_list.append({'description_field': var_name})

                write_data_tiff(file_name_list[var_id], file_data_list[var_id],
                                file_data_width, file_data_height, file_data_transform, file_epsg_code,
                                file_metadata=file_metadata_list[var_id], file_compression=file_compression_option)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write dataset
def write_dset_nc(file_name,
                  dset_data, dset_attrs=None,
                  dset_mode='w', dset_engine='h5netcdf', dset_compression=0, dset_format='NETCDF4',
                  dim_key_time='time', fill_data=-9999.0, dset_type='float32'):

    dset_encoded = dict(zlib=True, complevel=dset_compression, _FillValue=fill_data, dtype=dset_type)

    dset_encoding = {}
    for var_name in dset_data.data_vars:

        if isinstance(var_name, bytes):
            var_name_upd = var_name.decode("utf-8")
            dset_data = var_name.rename({var_name: var_name_upd})
            var_name = var_name_upd

        var_data = dset_data[var_name]
        var_attrs = deepcopy(dset_data[var_name].attrs)
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

                dset_data[var_name].attrs.pop(attr_key)

            if '_FillValue' not in list(dset_encoding[var_name].keys()):
                dset_encoding[var_name]['_FillValue'] = fill_data

            if '_FillValue' in list(dset_data[var_name].attrs.keys()):
                dset_data[var_name].attrs.pop['_FillValue']

    if dim_key_time in list(dset_data.coords):
        dset_encoding[dim_key_time] = {'calendar': 'gregorian'}

    dset_data.to_netcdf(path=file_name, format=dset_format, mode=dset_mode, engine=dset_engine,
                        encoding=dset_encoding)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a tmp name
def create_filename_tmp(prefix='tmp_', suffix='.tiff', folder=None):

    if folder is None:
        folder = '/tmp'

    with tempfile.NamedTemporaryFile(dir=folder, prefix=prefix, suffix=suffix, delete=False) as tmp:
        temp_file_name = tmp.name
    return temp_file_name
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data obj
def read_obj(file_name):
    if os.path.exists(file_name):
        data = pickle.load(open(file_name, "rb"))
    else:
        data = None
    return data
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write data obj
def write_obj(file_name, data):
    if os.path.exists(file_name):
        os.remove(file_name)
    with open(file_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
# -------------------------------------------------------------------------------------
