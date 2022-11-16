"""
Library Features:

Name:          lib_data_io_remap
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""
#################################################################################
# Library
import logging

import pandas as pd
import xarray as xr
import numpy as np
from copy import deepcopy

from tools.processing_tool_datasets_merger.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
# Debugging
import matplotlib.pylab as plt
#################################################################################


# --------------------------------------------------------------------------------
# Method to create dataset continuum format
def create_dset_continuum(
        var_time, var_dset_in,
        var_geo_values, var_geo_x, var_geo_y, var_geo_attrs=None, var_geo_name='terrain', var_geo_1d=False,
        var_data_attrs=None, var_file_attrs=None,
        coord_name_x='longitude', coord_name_y='latitude', coord_name_time='time',
        dims_order_2d=None, dims_order_3d=None,
        geo_x_dim_in='longitude', geo_y_dim_in='latitude', geo_time_dim_in='time',
        geo_x_dim_out='west_east', geo_y_dim_out='south_north', geo_time_dim_out='time'):

    if var_data_attrs is None:
        var_data_attrs = {}
    if var_file_attrs is None:
        var_file_attrs = {}

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
        dims_order_2d = [geo_y_dim_out, geo_x_dim_out]
    if dims_order_3d is None:
        dims_order_3d = [geo_y_dim_out, geo_x_dim_out, geo_time_dim_out]

    if isinstance(var_time, pd.Timestamp):
        var_data_time = pd.DatetimeIndex([var_time])
    elif isinstance(var_time, pd.DatetimeIndex):
        var_data_time = deepcopy(var_time)
    else:
        log_stream.error(' ===> Obj time format is not allowed')
        raise NotImplemented('Case not implemented yet')

    var_dset_out = xr.Dataset(coords={coord_name_time: ([geo_time_dim_out], var_data_time)})
    var_dset_out.coords[coord_name_time] = var_dset_out.coords[coord_name_time].astype('datetime64[ns]')

    var_geo_da = xr.DataArray(
        np.flipud(var_geo_values),  name=var_geo_name,
        dims=dims_order_2d,
        coords={coord_name_x: ([geo_y_dim_out, geo_x_dim_out], var_geo_x_tmp),
                coord_name_y: ([geo_y_dim_out, geo_x_dim_out], np.flipud(var_geo_y_tmp))}
    )
    var_dset_out[var_geo_name] = var_geo_da
    var_dset_out.attrs = {**var_geo_attrs, **var_file_attrs}

    for var_data_name in list(var_dset_in.variables):
        if var_data_name not in [geo_x_dim_in, geo_y_dim_in, geo_time_dim_in]:

            var_data_values = var_dset_in[var_data_name].values

            var_data_obj_attrs = var_dset_in[var_data_name].attrs

            if var_data_name in list(var_data_attrs.keys()):
                var_data_arg_attrs = var_data_attrs[var_data_name]
            else:
                var_data_arg_attrs = {}
            var_data_join_attrs = {**var_data_obj_attrs, **var_data_arg_attrs}

            if '_FillValue' not in list(var_data_join_attrs.keys()):
                var_data_join_attrs['_FillValue'] = {}

            no_data = var_data_join_attrs['_FillValue']
            var_data_values[np.isnan(var_data_values)] = no_data

            if var_data_values.ndim == 3 and var_data_values.shape[2] == 1:
                var_data_values = var_data_values.squeeze(axis=2)

            if var_data_values.ndim == 2:
                var_data_da = xr.DataArray(
                    np.flipud(var_data_values), name=var_data_name,
                    dims=dims_order_2d,
                    coords={coord_name_x: ([geo_y_dim_out, geo_x_dim_out], var_geo_x_tmp),
                            coord_name_y: ([geo_y_dim_out, geo_x_dim_out], np.flipud(var_geo_y_tmp))}
                )
            elif var_data_values.ndim == 3:

                var_data_da = xr.DataArray(
                    np.flipud(var_data_values), name=var_data_name,
                    dims=dims_order_3d,
                    coords={coord_name_time: ([geo_time_dim_out], var_time),
                            coord_name_x: ([geo_y_dim_out, geo_x_dim_out], var_geo_x_tmp),
                            coord_name_y: ([geo_y_dim_out, geo_x_dim_out], np.flipud(var_geo_y_tmp))})
            else:
                log_stream.error(' ===> Obj datasets format must be 1D or 2D')
                raise NotImplemented('Case not implemented yet')

            var_data_da.attrs = var_data_join_attrs
            var_dset_out[var_data_name] = var_data_da

    return var_dset_out

# --------------------------------------------------------------------------------

