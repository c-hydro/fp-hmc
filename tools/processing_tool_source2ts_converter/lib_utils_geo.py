"""
Library Features:

Name:          lib_utils_time
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""

#######################################################################################
# Libraries
import logging
import pandas as pd

from datetime import date

from lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to set geographical data
def set_geo(geo_obj):
    geo_ref_data = geo_obj['data']
    geo_ref_coord_x = geo_obj['geo_x']
    geo_ref_coord_y = geo_obj['geo_y']

    geo_ref_nrows = geo_obj['nrows']
    geo_ref_ncols = geo_obj['ncols']
    geo_ref_xll_corner = geo_ref_collections['xllcorner']
    geo_ref_yll_corner = geo_ref_collections['yllcorner']
    geo_ref_cellsize = geo_ref_collections['cellsize']
    geo_ref_nodata = geo_ref_collections['nodata_value']

    geo_ref_coord_x_2d, geo_ref_coord_y_2d = np.meshgrid(geo_ref_coord_x, geo_ref_coord_y)

    geo_y_upper = geo_ref_coord_y_2d[0, 0]
    geo_y_lower = geo_ref_coord_y_2d[-1, 0]
    if geo_y_lower > geo_y_upper:
        geo_ref_coord_y_2d = np.flipud(geo_ref_coord_y_2d)
        geo_ref_data = np.flipud(geo_ref_data)

    geo_da = xr.DataArray(
        geo_ref_data, name=geo_ref_name, dims=self.dims_order_2d,
        coords={self.coord_name_geo_x: (self.dim_name_geo_x, geo_ref_coord_x_2d[0, :]),
                self.coord_name_geo_y: (self.dim_name_geo_y, geo_ref_coord_y_2d[:, 0])})

    geo_da.attrs = {'ncols': geo_ref_ncols, 'nrows': geo_ref_nrows,
                    'nodata_value': geo_ref_nodata,
                    'xllcorner': geo_ref_xll_corner, 'yllcorner': geo_ref_yll_corner,
                    'cellsize': geo_ref_cellsize}

# -------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to set chunks
def set_chunks(time_range, time_period='D'):

    time_groups = time_range.to_period(time_period)
    time_chunks = time_range.groupby(time_groups)

    return time_chunks
# ----------------------------------------------------------------------------------------------------------------------
