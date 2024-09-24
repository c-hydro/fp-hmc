"""
Library Features:

Name:          lib_utils_method_interpolate
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""
# -------------------------------------------------------------------------------------
# Libraries
import logging
import pandas as pd
import xarray as xr
import numpy as np

from tools.processing_tool_datasets_merger.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to active interpolation method
def active_var_interpolate(var_attrs, geo_attrs, fields_included=None):

    if fields_included is None:
        fields_included = ['ncols', 'nrows', 'cellsize']

    active_interp = False
    for field_step in fields_included:
        if field_step in list(var_attrs.keys()):
            var_field_value = var_attrs[field_step]
        else:
            var_field_value = None
        if field_step in list(geo_attrs.keys()):
            geo_field_value = geo_attrs[field_step]
        else:
            geo_field_value = None

        if var_field_value is None:
            raise IOError('Attribute "' + field_step + '" in variable data array are not correctly defined')
        if geo_field_value is None:
            raise IOError('Attribute "' + field_step + '" in geo reference data array are not correctly defined')

        if var_field_value != geo_field_value:
            active_interp = True
            break

    return active_interp
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to apply interpolation method
def apply_var_interpolate(var_obj_in, geo_da_out,
                          dim_name_geo_x='longitude', dim_name_geo_y='latitude',
                          coord_name_geo_x='longitude', coord_name_geo_y='latitude',
                          interp_method='nearest'):

    if not isinstance(var_obj_in, (xr.DataArray, xr.Dataset)):
        raise RuntimeError('Data format for variable not allowed for applying the interpolation method')
    if not isinstance(geo_da_out, xr.DataArray):
        raise RuntimeError('Data format for geographical reference not allowed for applying the interpolation method')

    interp_dict = {dim_name_geo_y: geo_da_out[coord_name_geo_y], dim_name_geo_x: geo_da_out[coord_name_geo_x]}
    var_obj_out = var_obj_in.interp(interp_dict, method=interp_method)

    return var_obj_out

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to apply sample method
def apply_var_sample(var_dset_in, geo_da_out,
                     i_cols_ref, j_rows_ref, i_cols_dom, j_rows_dom,
                     dim_name_time='time', dim_name_geo_x='longitude', dim_name_geo_y='latitude',
                     coord_name_time='time', coord_name_geo_x='longitude', coord_name_geo_y='latitude'):

    dims_list_expected = [dim_name_geo_y, dim_name_geo_x, dim_name_time]
    coords_list_expected = [coord_name_time, coord_name_geo_x, coord_name_geo_y]

    dims_list_in = list(var_dset_in.dims)
    coords_list_in = list(var_dset_in.coords)
    variable_list_in = list(var_dset_in.variables)

    if set(dims_list_in) != set(dims_list_expected):
        log_stream.error(' ===> Dimensions expected and found in the datasets are different')
        raise RuntimeError('Dimensions must be the same to avoid errors in output datasets')
    if set(coords_list_in) != set(coords_list_expected):
        log_stream.error(' ===> Coordinates expected and found in the datasets are different')
        raise RuntimeError('Coordinates must be the same to avoid errors in output datasets')

    # check dimensions order
    dims_order, dims_check = {}, False
    for dims_id, dims_step_in in enumerate(dims_list_in):
        dims_step_expected = dims_list_expected[dims_id]
        if dims_step_in == dims_step_expected:
            dims_order[dims_id] = dims_step_in
        else:
            dims_idx_expected = dims_list_expected.index(dims_step_in)
            dims_order[dims_idx_expected] = dims_step_in
            dims_check = True

    if dims_check:
        dims_list_defined = [dim_name_geo_y, dim_name_geo_x, dim_name_time]
        log_stream.warning(' ===> Dimensions expected (1) are not in the same order of datasets dimensions (2)')
        log_stream.warning(' ===> (1) Dimensions expected: ' + ','.join(dims_list_expected))
        log_stream.warning(' ===> (2) Dimensions datasets: ' + ','.join(list(var_dset_in.dims)))
        log_stream.warning(' ===> Dimensions selected by constants: ' + ','.join(dims_list_expected))
    else:
        dims_list_defined = list(var_dset_in.dims)

    geo_x_out = geo_da_out['longitude'].values
    geo_y_out = geo_da_out['latitude'].values

    geo_attrs_out = geo_da_out.attrs

    i_cols_ref, j_rows_ref = i_cols_ref.astype(int), j_rows_ref.astype(int)
    i_cols_dom, j_rows_dom = i_cols_dom.astype(int), j_rows_dom.astype(int)

    flag_time = False
    if dim_name_time in dims_list_in and coord_name_time in coords_list_in:
        flag_time = True

    if flag_time:
        variable_time = pd.DatetimeIndex(var_dset_in[coord_name_time].values)
        if variable_time.shape[0] == 1:
            var_dset_out = xr.Dataset(coords={coord_name_time: ([dim_name_time], variable_time)})
            var_dset_out.coords[coord_name_time] = var_dset_out.coords[coord_name_time].astype('datetime64[ns]')
            var_dset_out.attrs = geo_attrs_out
        else:
            log_stream.error(' ===> Sample datasets is expected with time coordinate equal to 1')
            raise NotImplementedError('Case not implemented yet')
    else:
        variable_time = None
        var_dset_out = xr.Dataset()
        var_dset_out.attrs = geo_attrs_out

    var_dict_tmp = {}
    for variable_name in variable_list_in:

        var_values_tmp = np.zeros(shape=[geo_da_out.shape[0], geo_da_out.shape[1]])
        var_values_tmp[:, :] = np.nan

        if variable_name not in coords_list_in:
            var_values_in = var_dset_in[variable_name].values

            for i_dom, j_dom in zip(i_cols_dom.flatten(), j_rows_dom.flatten()):
                if i_dom >= 0 and j_dom >= 0:
                    i_cols_tmp = i_cols_ref[i_dom, j_dom]
                    j_rows_tmp = j_rows_ref[i_dom, j_dom]

                    var_values_tmp[j_rows_tmp, i_cols_tmp] = var_values_in[i_dom, j_dom]

            var_dict_tmp[variable_name] = var_values_tmp

    for variable_name, variable_data in var_dict_tmp.items():

        if variable_time is not None:

            if variable_data.shape.__len__() < coords_list_in.__len__():
                variable_data = variable_data[:, :, np.newaxis]
            elif variable_data.shape.__len__() == coords_list_in.__len__():
                pass
            else:
                log_stream.error(' ===> Expected variable data must be <= coords shape')
                raise NotImplemented('Case not implemented yet')

            var_da_tmp = xr.DataArray(
                variable_data, name=variable_name, dims=dims_list_defined,
                coords={coord_name_time: ([dim_name_time], variable_time),
                        coord_name_geo_x: ([dim_name_geo_x], geo_x_out),
                        coord_name_geo_y: ([dim_name_geo_y], geo_y_out)})
            var_dset_out[variable_name] = var_da_tmp

        else:
            var_da_tmp = xr.DataArray(
                variable_data, name=variable_name, dims=dims_list_defined,
                coords={coord_name_geo_x: ([dim_name_geo_x], geo_x_out),
                        coord_name_geo_y: ([dim_name_geo_y], geo_y_out)})
            var_dset_out[variable_name] = var_da_tmp

    # Debug
    # variable_data = var_dset_out['LST'].values
    # plt.figure()
    # plt.imshow(variable_data[:, :, 0])
    # plt.colorbar()
    # plt.show()

    return var_dset_out

# -------------------------------------------------------------------------------------
