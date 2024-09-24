"""
Class Features

Name:          lib_data_io_tiff
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20221013'
Version:       '1.1.0'
"""

#######################################################################################
# Libraries
import logging
import os
import rasterio

import numpy as np
import xarray as xr
import pandas as pd

from copy import deepcopy
from rasterio.transform import Affine
from osgeo import gdal, gdalconst

from tools.processing_tool_datasets_merger.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
#######################################################################################

# -------------------------------------------------------------------------------------
# Default settings
proj_default_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write data tiff
def write_data_tiff(file_name, file_data, file_wide, file_high, file_geotrans, file_proj,
                    file_metadata=None, file_compression='COMPRESS=DEFLATE',
                    file_format=gdalconst.GDT_Float32):

    if not isinstance(file_data, list):
        file_data = [file_data]

    if file_metadata is None:
        file_metadata = {'description_field': 'data'}
    if not isinstance(file_metadata, list):
        file_metadata = [file_metadata] * file_data.__len__()

    if isinstance(file_geotrans, Affine):
        file_geotrans = file_geotrans.to_gdal()

    file_crs = rasterio.crs.CRS.from_string(file_proj)
    file_wkt = file_crs.to_wkt()

    file_n = file_data.__len__()
    dset_handle = gdal.GetDriverByName('GTiff').Create(file_name, file_wide, file_high, file_n, file_format,
                                                       options=[file_compression])
    dset_handle.SetGeoTransform(file_geotrans)
    dset_handle.SetProjection(file_wkt)

    for file_id, (file_data_step, file_metadata_step) in enumerate(zip(file_data, file_metadata)):
        dset_handle.GetRasterBand(file_id + 1).WriteArray(file_data_step)
        dset_handle.GetRasterBand(file_id + 1).SetMetadata(file_metadata_step)
    del dset_handle
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data
def read_data_tiff(file_name, var_scale_factor=1, var_type='float32', var_name=None, var_time=None, var_no_data=-9999.0,
                   coord_name_time='time', coord_name_geo_x='Longitude', coord_name_geo_y='Latitude',
                   dim_name_time='time', dim_name_geo_x='west_east', dim_name_geo_y='south_north',
                   dims_order=None,
                   decimal_round_data=7, flag_round_data=False,
                   decimal_round_geo=7, flag_round_geo=True,
                   flag_obj_type='DataArray'):

    if dims_order is None:
        dims_order = [dim_name_geo_y, dim_name_geo_x, dim_name_time]

    if isinstance(var_no_data, str):
        pass
    elif isinstance(var_no_data, list) and var_no_data.__len__() == 1:
        var_no_data = var_no_data[0]
    else:
        log_stream.error(' ===> The arguments "var_no_data" must be a string or a list with length equal to 1')
        raise NotImplemented('Case not implemented yet')
    if isinstance(var_name, str):
        pass
    elif isinstance(var_name, list) and var_name.__len__() == 1:
        var_name = var_name[0]
    else:
        log_stream.error(' ===> The arguments "var_name" must be a string or a list with length equal to 1')
        raise NotImplemented('Case not implemented yet')
    if isinstance(var_type, str):
        pass
    elif isinstance(var_type, list) and var_type.__len__() == 1:
        var_type = var_type[0]
    else:
        log_stream.error(' ===> The arguments "var_type" must be a string or a list with length equal to 1')
        raise NotImplemented('Case not implemented yet')
    if isinstance(var_scale_factor, str):
        pass
    elif isinstance(var_scale_factor, list) and var_scale_factor.__len__() == 1:
        var_scale_factor = var_scale_factor[0]
    else:
        log_stream.error(' ===> The arguments "var_scale_factor" must be a string or a list with length equal to 1')
        raise NotImplemented('Case not implemented yet')

    if os.path.exists(file_name):
        # Open file tiff
        file_handle = rasterio.open(file_name)
        # Read file info and values
        file_bounds = file_handle.bounds
        file_res = file_handle.res
        file_transform = file_handle.transform
        file_nodata = file_handle.nodata
        file_data = file_handle.read()
        file_attrs = file_handle.meta
        file_values = file_data[0, :, :]

        if file_nodata is None:
            file_nodata = var_no_data

        if flag_round_data:
            file_values = file_values.round(decimal_round_data)

        if var_type == 'float64':
            file_values = np.float64(file_values / var_scale_factor)
        elif var_type == 'float32':
            file_values = np.float32(file_values / var_scale_factor)
        else:
            log_stream.error(' ===> File type is not correctly defined.')
            raise NotImplemented('Case not implemented yet')

        if file_handle.crs is None:
            file_proj = proj_default_wkt
            log_stream.warning(' ===> Projection of tiff ' + file_name + ' not defined. Use constants settings.')
        else:
            file_proj = file_handle.crs.wkt
        file_geotrans = file_handle.transform

        file_dims = file_values.shape
        file_high = file_dims[0]
        file_wide = file_dims[1]

        center_right = file_bounds.right - (file_res[0] / 2)
        center_left = file_bounds.left + (file_res[0] / 2)
        center_top = file_bounds.top - (file_res[1] / 2)
        center_bottom = file_bounds.bottom + (file_res[1] / 2)

        if center_bottom > center_top:
            center_bottom_tmp = center_top
            center_top_tmp = center_bottom
            center_bottom = center_bottom_tmp
            center_top = center_top_tmp

            file_values = np.flipud(file_values)

        lon = np.arange(center_left, center_right + np.abs(file_res[0] / 2), np.abs(file_res[0]), float)
        lat = np.flip(np.arange(center_bottom, center_top + np.abs(file_res[1] / 2), np.abs(file_res[1]), float))
        lons, lats = np.meshgrid(lon, lat)

        if flag_round_geo:
            min_lon_round = round(np.min(lons), decimal_round_geo)
            max_lon_round = round(np.max(lons), decimal_round_geo)
            min_lat_round = round(np.min(lats), decimal_round_geo)
            max_lat_round = round(np.max(lats), decimal_round_geo)

            center_right_round = round(center_right, decimal_round_geo)
            center_left_round = round(center_left, decimal_round_geo)
            center_bottom_round = round(center_bottom, decimal_round_geo)
            center_top_round = round(center_top, decimal_round_geo)
        else:
            log_stream.error(' ===> Switch off the rounding of geographical dataset is not expected')
            raise NotImplemented('Case not implemented yet')

        assert min_lon_round == center_left_round
        assert max_lon_round == center_right_round
        assert min_lat_round == center_bottom_round
        assert max_lat_round == center_top_round

        var_geo_x_2d, var_geo_y_2d = lons, lats
        if dims_order.__len__() == 3:
            var_data = np.zeros(shape=[var_geo_x_2d.shape[0], var_geo_y_2d.shape[1], 1])
            var_data[:, :, :] = np.nan
            var_data[:, :, 0] = file_values
        elif dims_order.__len__() == 2:
            var_data = np.zeros(shape=[var_geo_x_2d.shape[0], var_geo_y_2d.shape[1]])
            var_data[:, :] = np.nan
            var_data[:, :] = file_values
        else:
            log_stream.error(' ===> Variable dimensions is not allowed. Only 2D or 3D variables are configured.')
            raise NotImplemented('Case not implemented yet')

        geo_attrs = {'nrows': var_geo_y_2d.shape[0], 'ncols': var_geo_x_2d.shape[1],
                     'nodata_value': file_nodata,
                     'xllcorner': file_transform[2],
                     'yllcorner': file_transform[5], 'cellsize': abs(file_transform[0]),
                     'proj': file_proj, 'transform': file_geotrans}

    else:
        log_stream.warning(' ===> File ' + file_name + ' not available in loaded datasets!')
        var_data, geo_attrs, var_geo_x_2d, var_geo_y_2d = None, None, None, None

    if var_data is not None:

        if var_time is not None:
            if dims_order.__len__() == 3:
                if isinstance(var_time, pd.Timestamp):
                    var_data_time = pd.DatetimeIndex([var_time])
                elif isinstance(var_time, pd.DatetimeIndex):
                    var_data_time = deepcopy(var_time)
                else:
                    log_stream.error(' ===> Time format is not allowed. Expected Timestamp or Datetimeindex')
                    raise NotImplemented('Case not implemented yet')

                if flag_obj_type == 'DataArray':
                    var_obj = xr.DataArray(var_data, name=var_name, dims=dims_order,
                                           coords={coord_name_time: ([dim_name_time], var_data_time),
                                                   coord_name_geo_x: ([dim_name_geo_x], var_geo_x_2d[0, :]),
                                                   coord_name_geo_y: ([dim_name_geo_y], var_geo_y_2d[:, 0])})

                elif flag_obj_type == 'Dataset':

                    var_obj = xr.Dataset(coords={coord_name_time: ([dim_name_time], var_data_time)})
                    var_obj.coords[coord_name_time] = var_obj.coords[coord_name_time].astype('datetime64[ns]')

                    var_tmp = xr.DataArray(var_data, name=var_name, dims=dims_order,
                                           coords={coord_name_time: ([dim_name_time], var_data_time),
                                                   coord_name_geo_x: ([dim_name_geo_x], var_geo_x_2d[0, :]),
                                                   coord_name_geo_y: ([dim_name_geo_y], var_geo_y_2d[:, 0])})
                    var_obj[var_name] = var_tmp

                else:
                    log_stream.error(' ===> DataObj type must be "DataArray" or "Dataset"')
                    raise NotImplemented('Case not implemented yet')

            elif dims_order.__len__() == 2:

                if flag_obj_type == 'DataArray':

                    var_obj = xr.DataArray(var_data, name=var_name, dims=dims_order,
                                           coords={coord_name_geo_x: ([dim_name_geo_x], var_geo_x_2d[0, :]),
                                                   coord_name_geo_y: ([dim_name_geo_y], var_geo_y_2d[:, 0])})

                elif flag_obj_type == 'DataSet':
                    var_obj = xr.Dataset()
                    var_tmp = xr.DataArray(var_data, name=var_name, dims=dims_order,
                                           coords={coord_name_geo_x: ([dim_name_geo_x], var_geo_x_2d[0, :]),
                                                   coord_name_geo_y: ([dim_name_geo_y], var_geo_y_2d[:, 0])})
                    var_obj[var_name] = var_tmp

                else:
                    log_stream.error(' ===> DataObj type must be "DataArray" or "Dataset"')
                    raise NotImplemented('Case not implemented yet')

            else:
                log_stream.error(' ===> DataObj dims must be 2D or 3D')
                raise NotImplemented('Case not implemented yet')

            if file_attrs and geo_attrs:
                obj_attrs = {**file_attrs, **geo_attrs}
            elif (not file_attrs) and geo_attrs:
                obj_attrs = deepcopy(geo_attrs)
            elif file_attrs and (not geo_attrs):
                obj_attrs = deepcopy(file_attrs)
            else:
                obj_attrs = None

            if obj_attrs is not None:
                var_obj.attrs = obj_attrs

        elif var_time is None:
            log_stream.error(' ===> Time must be defined by DateTimeIndex format and not by NoneType')
            raise RuntimeError('Case not implemented yet')
        else:
            log_stream.error(' ===> Error in creating time information for dataset object')
            raise RuntimeError('Unknown error in creating dataset. Check the procedure.')

    else:
        log_stream.warning(' ===> All filenames in the selected period are not available')
        var_obj = None

    return var_obj

# -------------------------------------------------------------------------------------
