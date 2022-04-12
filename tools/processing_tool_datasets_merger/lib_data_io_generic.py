"""
Library Features:

Name:          lib_data_io_generic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""
#######################################################################################
# Library
import logging
import os
import json

from tools.processing_tool_datasets_merger.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to extract data grid information
def extract_data_grid(geo_data, geo_x_values, geo_y_values, geo_transform, geo_bbox=None,
                      tag_geo_values='data',
                      tag_geo_x='geo_x', tag_geo_y='geo_y',
                      tag_nodata='nodata_value', value_no_data=-9999.0):

    if geo_bbox is not None:
        geo_bbox_xll = geo_bbox[0]
        geo_bbox_yll = geo_bbox[1]
        data_grid = {'nrows': geo_y_values.shape[0], 'ncols': geo_x_values.shape[0], 'xllcorner': geo_bbox_xll,
                     'yllcorner': geo_bbox_yll, 'cellsize': abs(geo_transform[0]), tag_geo_values: geo_data,
                     tag_geo_x: geo_x_values, tag_geo_y: geo_y_values}
    elif geo_bbox is None:
        data_grid = {'nrows': geo_y_values.shape[0], 'ncols': geo_x_values.shape[0], 'xllcorner': geo_transform[0],
                     'yllcorner': geo_transform[3], 'cellsize': abs(geo_transform[1]), tag_geo_values: geo_data,
                     tag_geo_x: geo_x_values, tag_geo_y: geo_y_values}

    if tag_nodata not in list(data_grid.keys()):
        data_grid[tag_nodata] = value_no_data

    return data_grid
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to parse data_grid
def parse_data_grid(var_da):

    var_values = var_da.values
    var_attrs = var_da.attrs

    var_geo_x = None
    for var_geo_x_step in ['longitude', 'Longitude']:
        if var_geo_x_step in list(list(var_da.coords.variables)):
            var_geo_x = var_da[var_geo_x_step].values
            break
    if var_geo_x is None:
        raise IOError('Longitude variable is is not available or not defined')
    var_geo_y = None
    for var_geo_y_step in ['latitude', 'Latitude']:
        if var_geo_y_step in list(list(var_da.coords.variables)):
            var_geo_y = var_da[var_geo_y_step].values
            break
    if var_geo_y is None:
        raise IOError('Latitude variable is is not available or not defined')

    if 'ncols' in list(var_attrs.keys()):
        var_geo_x_n = int(var_attrs['ncols'])
    else:
        var_geo_x_n = var_values.shape[1]

    if 'nrows' in list(var_attrs.keys()):
        var_geo_y_n = int(var_attrs['nrows'])
    else:
        var_geo_y_n = var_values.shape[0]

    if ('xllcorner' in list(var_attrs.keys()) and 'yllcorner' in list(var_attrs.keys())) and \
            ('cellsize' in list(var_attrs.keys())):
        var_geo_x_min = var_attrs['xllcorner']
        var_geo_y_max = var_attrs['yllcorner']
        var_geo_x_res = var_attrs['cellsize']
        var_geo_y_res = var_attrs['cellsize']
    else:
        var_geo_x_min, var_geo_y_min, var_geo_x_max, var_geo_y_max = [var_geo_x.min(), var_geo_y.min(),
                                                                      var_geo_x.max(), var_geo_y.max()]

        var_geo_x_res = (var_geo_x_max - var_geo_x_min) / float(var_geo_x_n)
        var_geo_y_res = (var_geo_y_max - var_geo_y_min) / float(var_geo_y_n)

    var_geo_transform = (var_geo_x_min, var_geo_x_res, 0, var_geo_y_max, 0, -var_geo_y_res)

    return var_values, var_geo_x, var_geo_y, var_geo_transform
# -------------------------------------------------------------------------------------
