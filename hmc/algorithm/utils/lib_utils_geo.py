"""
Library Features:

Name:          lib_utils_geo
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#################################################################################
# Libraries
import logging
import pyproj

from pysheds.grid import Grid
import numpy as np

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
#################################################################################


# --------------------------------------------------------------------------------
# Method to define section mask
def compute_section_mask(fdir_values, fdir_map=None, fdir_nodata=0, geo_reference=None, section_reference=None):

    if fdir_map is None:
        fdir_map = [8, 9, 6, 3, 2, 1, 4, 7]

    geo_values = geo_reference['values']
    geo_longitude = geo_reference['longitude']
    geo_latitude = geo_reference['latitude']
    geo_transform = geo_reference['transform']
    geo_crs = geo_reference['crs']

    mask_values = np.zeros([fdir_values.shape[0], fdir_values.shape[1]], dtype=bool)
    mask_values[:, :] = True

    grid = Grid()
    grid.add_gridded_data(data=fdir_values, data_name='fdir',
                          affine=geo_transform,
                          crs=pyproj.Proj(geo_crs),
                          nodata=fdir_nodata)
    grid.add_gridded_data(data=mask_values, data_name='mask',
                          affine=geo_transform,
                          crs=pyproj.Proj(geo_crs),
                          nodata=False)

    section_obj = {}
    for section_tag, section_fields in section_reference.items():
        section_idx_ji = section_fields['section_idx_ji']
        section_j = section_idx_ji[0] - 1
        section_i = section_idx_ji[1] - 1
        section_mask = 'section_mask'

        grid.catchment(data=grid.fdir, x=section_i, y=section_j,
                       dirmap=fdir_map, out_name=section_mask,
                       recursionlimit=15000, nodata_out=0, ytype='index')
        section_mask = np.array(grid.section_mask).astype(np.float32)

        section_mask[section_mask == 0] = 0
        section_mask[geo_values < 0] = 0
        section_mask[section_mask >= 1] = 1

        geo_latitude = np.flipud(geo_latitude)

        section_da = create_darray_2d(section_mask, geo_longitude, geo_latitude,
                                      coord_name_x='Longitude', coord_name_y='Latitude',
                                      dim_name_x='west_east', dim_name_y='south_north',
                                      dims_order=['south_north', 'west_east'])

        section_obj[section_tag] = {}
        section_obj[section_tag] = section_da

    return section_obj

# --------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create a data array
def create_darray_2d(data, geo_x, geo_y, geo_1d=True, time=None,
                     coord_name_x='west_east', coord_name_y='south_north', coord_name_time='time',
                     dim_name_x='west_east', dim_name_y='south_north', dim_name_time='time',
                     dims_order=None):
    import xarray as xr
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


# --------------------------------------------------------------------------------
# Method to convert curve number to maximum volume
def compute_cn2vmax(curve_number):

    # Initialize volume max
    volume_max = np.zeros([curve_number.shape[0], curve_number.shape[1]])
    volume_max[:, :] = np.nan

    # Compute volume max starting from curve number values
    volume_max = (1000/curve_number - 10) * 25.4

    return volume_max

# --------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compute cell area in m^2
def compute_cell_area(geo_x, geo_y, cell_size_x, cell_size_y):

    # Method constant(s)
    r = 6378388  # (Radius)
    e = 0.00672267  # (Ellipsoid)

    # dx = (R * cos(lat)) / (sqrt(1 - e2 * sqr(sin(lat)))) * PI / 180
    dx_2d = (r * np.cos(np.abs(geo_y) * np.pi / 180)) / \
            (np.sqrt(1 - e * np.sqrt(np.sin(np.abs(geo_y) * np.pi / 180)))) * np.pi / 180
    # dy = (R * (1 - e2)) / pow((1 - e2 * sqr(sin(lat))),1.5) * PI / 180
    dy_2d = (r * (1 - e)) / np.power((1 - e * np.sqrt(np.sin(np.abs(geo_y) / 180))), 1.5) * np.pi / 180

    # area cell  in m^2
    area_cell = ((dx_2d / (1 / cell_size_x)) * (dy_2d / (1 / cell_size_y)))  # [m^2]

    return area_cell

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compute drainage area in m^2 or Km^2
def compute_drainage_area(terrain, cell_area, no_data=-9999, units='Km^2'):

    cell_n = np.where(terrain.ravel() != no_data)[0].size
    drainage_area = cell_n * cell_area

    if units == 'Km^2':
        drainage_area = drainage_area / 1000000
    elif units == 'm^2':
        pass
    else:
        log_stream.error(' ===> Drainage area units are not allowed')
        raise IOError('Drainage area units are wrongly defined. Check your settings.')

    return drainage_area

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compute corrivation time
def compute_corrivation_time(geo_values, geo_x, geo_y, cell_size_x, cell_size_y):

    # Dynamic values
    r = 6378388  # (Radius)
    e = 0.00672267  # (Ellipsoid)

    # dx = (R * cos(lat)) / (sqrt(1 - e2 * sqr(sin(lat)))) * PI / 180
    dx_2d = (r * np.cos(np.abs(geo_y) * np.pi / 180)) / \
            (np.sqrt(1 - e * np.sqrt(np.sin(np.abs(geo_y) * np.pi / 180)))) * np.pi / 180

    # dy = (R * (1 - e2)) / pow((1 - e2 * sqr(sin(lat))),1.5) * PI / 180
    dy_2d = (r * (1 - e)) / np.power((1 - e * np.sqrt(np.sin(np.abs(geo_y) / 180))), 1.5) * np.pi / 180

    # area cell in m^2
    area_cell = ((dx_2d / (1 / cell_size_x)) * (dy_2d / (1 / cell_size_y)))  # [m^2]

    # Area, Mean Dx and Dy values (meters)
    dx_avg = np.sqrt(np.nanmean(area_cell))
    dy_avg = np.sqrt(np.nanmean(area_cell))

    # Compute domain pixels and area
    pixels_n = np.sum(np.isfinite(geo_values))
    area_tot = float(pixels_n) * dx_avg * dy_avg / 1000000

    # Corrivation time [hour]
    tc = np.int(0.27 * np.sqrt(0.6 * area_tot) + 0.25)

    return tc
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to clip data 2D/3D using a min/max threshold(s) and assign a missing value
def clip_map(map, valid_range=None, missing_value=None):

    # Set variable valid range
    if valid_range is None:
        valid_range = [None, None]

    if valid_range is not None:
        if valid_range[0] is not None:
            valid_range_min = float(valid_range[0])
        else:
            valid_range_min = None
        if valid_range[1] is not None:
            valid_range_max = float(valid_range[1])
        else:
            valid_range_max = None
        # Set variable missing value
        if missing_value is None:
            missing_value_min = valid_range_min
            missing_value_max = valid_range_max
        else:
            missing_value_min = missing_value
            missing_value_max = missing_value

        # Apply min and max condition(s)
        if valid_range_min is not None:
            map = map.where(map >= valid_range_min, missing_value_min)
        if valid_range_max is not None:
            map = map.where(map <= valid_range_max, missing_value_max)

        return map
    else:
        return map

# -------------------------------------------------------------------------------------
