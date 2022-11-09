"""
Class Features

Name:          lib_data_geo_ascii
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Libraries
import logging
import rasterio
import os

import numpy as np

from copy import deepcopy
from rasterio.crs import CRS
from collections import OrderedDict
from decimal import Decimal

from hmc.algorithm.io.lib_data_io_generic import create_darray_2d

from hmc.algorithm.utils.lib_utils_system import create_folder
from hmc.algorithm.utils.lib_utils_list import pad_or_truncate_list
from hmc.algorithm.utils.lib_utils_string import parse_row2string
from hmc.algorithm.default.lib_default_args import logger_name
from hmc.algorithm.default.lib_default_args import proj_epsg as proj_epsg_default

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to write file point section(s)
def write_data_point_section(file_name, file_data, file_cols_expected=11, file_name_expected=None):

    if file_name_expected is None:
        file_name_expected = ['section_idx_j', 'section_idx_i', 'section_domain', 'section_name',
                              'section_code', 'section_drained_area',
                              'section_discharge_thr_alert', 'section_discharge_thr_alarm', 'section_discharge_thr_emergency',
                              'section_reference', 'section_baseflow']

    file_data_expected = {}
    for file_key, file_fields in file_data.items():
        file_data_expected[file_key] = {}
        for field_key, field_value in file_fields.items():
            if field_key in file_name_expected:
                file_data_expected[file_key][field_key] = field_value
    file_data = deepcopy(file_data_expected)

    if isinstance(file_data, dict):
        file_keys = list(file_data.keys())
        if file_keys.__len__() >= 1:
            for file_key in file_keys:
                file_fields = file_data[file_key]
                if isinstance(file_fields, dict):
                    cols = file_fields.__len__()
                    break
                else:
                    log_stream.error(' ===> Fields obj is not in a dictionary format.')
                    raise NotImplementedError('Case not implemented yet')
        else:
            cols = None
            log_stream.warning(' ===> Section list is equal to zero. No file section will be dumped.')
    else:
        log_stream.error(' ===> Section data obj is not in a dictionary format.')
        raise NotImplementedError('Case not implemented yet')

    # cols = file_data.__len__() --> previous
    if cols != file_cols_expected:
        log_stream.error(' ===> File sections columns ' + str(cols) + ' found != columns expected ' +
                         str(file_cols_expected))
        raise IOError('File datasets are in a wrong format')

    if cols is not None:

        file_obj = []
        for key in file_keys:
            if isinstance(file_data, dict):
                row = list(file_data[key].values())
            else:
                log_stream.error(' ===> Section data obj is not in a dictionary format.')
                raise NotImplementedError('Case not implemented yet')

            file_obj.append(row)

        file_folder = os.path.split(file_name)[0]
        create_folder(file_folder)
        with open(file_name, "w", encoding='utf-8') as file:
            for file_row in file_obj:
                string_row = ' '.join(str(item) for item in file_row)
                string_row = string_row + '\n'
                file.write(string_row)
    else:
        log_stream.warning(' ===> Section data is None type. The file section will be undefined.')
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file point section(s)
def read_data_point_section(file_name, section_cols_expected=8):

    file_handle = open(file_name, 'r')
    file_lines = file_handle.readlines()
    file_handle.close()

    if file_lines.__len__() >= 1:

        string_parts = None

        point_frame = OrderedDict()
        for row_id, row_data in enumerate(file_lines):

            # Read line by line
            section_row = row_data.strip()
            # Clean unnecessary string delimiter ""
            section_row = section_row.replace('"', '')
            # Split string to cell(s)
            section_cols = section_row.split()

            if section_row != '':
                if string_parts is None:
                    string_parts = section_cols.__len__()

                if section_cols.__len__() > string_parts:
                    log_stream.error(' ===> Parse section filename failed for filename ' + os.path.split(file_name)[1])
                    raise IOError(' ===> Section file in wrong format: [fields: "'
                                  + section_row + '" at line ' + str(row_id + 1) + ']')

                if section_cols.__len__() < section_cols_expected:
                    section_cols = pad_or_truncate_list(section_cols, section_cols_expected)

                section_idx_ji = [int(section_cols[0]), int(section_cols[1])]
                section_domain = section_cols[2]
                section_name = section_cols[3]

                if isinstance(section_cols[4], (float, int)):
                    section_code = int(section_cols[4])
                elif isinstance(section_cols[4], str):
                    section_code = section_cols[4]
                else:
                    log_stream.error(
                        ' ===> Parse section filename failed in filtering "section code" value "' + section_cols[4] +
                        '". Value types allowed are float, int and string')
                    raise IOError('Case not implemented yet')

                section_drained_area = float(section_cols[5])
                section_discharge_thr_alert = float(section_cols[6])
                section_discharge_thr_alarm = float(section_cols[7])
                section_discharge_thr_emergency = float(section_cols[8])
                section_id = int(row_id)

                section_key = ':'.join([section_domain, section_name])

                point_frame[section_key] = {}
                point_frame[section_key]['section_id'] = section_id
                point_frame[section_key]['section_name'] = section_name
                point_frame[section_key]['section_domain'] = section_domain
                point_frame[section_key]['section_idx_ji'] = section_idx_ji
                point_frame[section_key]['section_code'] = section_code
                point_frame[section_key]['section_drained_area'] = section_drained_area
                point_frame[section_key]['section_discharge_thr_alert'] = section_discharge_thr_alert
                point_frame[section_key]['section_discharge_thr_alarm'] = section_discharge_thr_alarm
                point_frame[section_key]['section_discharge_thr_emergency'] = section_discharge_thr_emergency

            else:
                log_stream.error(' ===> Parse section filename failed for filename ' + os.path.split(file_name)[1])
                raise IOError(' ===> Section file in empty format: [fields: "'
                              + section_row + '" at line ' + str(row_id + 1) + ']')

    else:

        log_stream.warning(' ===> File info for sections was found; sections are equal to zero. Datasets is None')
        log_stream.warning(' ===> Filename ' + os.path.split(file_name)[1])
        point_frame = None

    return point_frame
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file point dam(s)
def read_data_point_dam(file_name, line_delimiter='#'):

    file_handle = open(file_name, 'r')
    file_lines = file_handle.readlines()
    file_handle.close()

    row_id = 0
    dam_n = int(file_lines[row_id].split(line_delimiter)[0])
    row_id += 1
    plant_n = int(file_lines[row_id].split(line_delimiter)[0])

    if dam_n > 0:

        point_frame = None
        for dam_id in range(0, dam_n):
            row_id += 1
            _ = parse_row2string(file_lines[row_id], line_delimiter)
            row_id += 1
            dam_name = parse_row2string(file_lines[row_id], line_delimiter)
            row_id += 1
            dam_idx_ji = list(map(int, parse_row2string(file_lines[row_id], line_delimiter).split()))
            row_id += 1
            dam_plant_n = int(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            dam_cell_lake_code = int(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            dam_volume_max = float(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            dam_volume_init = float(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            dam_discharge_max = float(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            dam_level_max = float(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            dam_h_max = float(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            dam_lin_coeff = float(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            dam_storage_curve = parse_row2string(file_lines[row_id], line_delimiter)

            for plant_id in range(0, int(dam_plant_n)):
                row_id += 1
                plant_name = parse_row2string(file_lines[row_id], line_delimiter)
                row_id += 1
                plant_idx_ji = list(map(int, parse_row2string(file_lines[row_id], line_delimiter).split()))
                row_id += 1
                plant_tc = int(parse_row2string(file_lines[row_id], line_delimiter))
                row_id += 1
                plant_discharge_max = float(parse_row2string(file_lines[row_id], line_delimiter))
                row_id += 1
                plant_discharge_flag = int(parse_row2string(file_lines[row_id], line_delimiter))

                # define dam and plant tag(s)
                if plant_name != '':
                    dam_key = ':'.join([dam_name, plant_name])
                else:
                    plant_name = 'plant_{:}'.format(plant_id)
                    dam_key = ':'.join([dam_name, plant_name])

                if point_frame is None:
                    point_frame = OrderedDict()
                if dam_key not in list(point_frame.keys()):
                    point_frame[dam_key] = {}
                    point_frame[dam_key]['dam_name'] = dam_name
                    point_frame[dam_key]['dam_idx_ji'] = dam_idx_ji
                    point_frame[dam_key]['dam_plant_n'] = dam_plant_n
                    point_frame[dam_key]['dam_lake_code'] = dam_cell_lake_code
                    point_frame[dam_key]['dam_volume_max'] = dam_volume_max
                    point_frame[dam_key]['dam_volume_init'] = dam_volume_init
                    point_frame[dam_key]['dam_discharge_max'] = dam_discharge_max
                    point_frame[dam_key]['dam_level_max'] = dam_level_max
                    point_frame[dam_key]['dam_h_max'] = dam_h_max
                    point_frame[dam_key]['dam_lin_coeff'] = dam_lin_coeff
                    point_frame[dam_key]['dam_storage_curve'] = dam_storage_curve

                    point_frame[dam_key]['plant_name'] = plant_name
                    point_frame[dam_key]['plant_idx_ji'] = plant_idx_ji
                    point_frame[dam_key]['plant_tc'] = plant_tc
                    point_frame[dam_key]['plant_discharge_max'] = plant_discharge_max
                    point_frame[dam_key]['plant_discharge_flag'] = plant_discharge_flag
                else:
                    log_stream.error(' ===> Dam name "' + dam_key + '" is already saved in the obj structure ')
                    raise IOError('Key value must be different for adding it in the dam object')

    else:

        log_stream.warning(' ===> File info for dams was found; dams are equal to zero. Datasets is None')
        log_stream.warning(' ===> Filename ' + os.path.split(file_name)[1])
        point_frame = None

    if point_frame is not None:
        point_frame_reorder, point_frame_root = {}, []
        for point_key, point_fields in point_frame.items():

            point_name_root, point_name_other = point_key.split(':')

            if point_name_root not in point_frame_root:
                point_frame_reorder[point_key] = point_fields
                point_frame_root.append(point_name_root)
            else:
                point_idx_root = point_frame_root.index(point_name_root)

                point_key_root = list(point_frame_reorder.keys())[point_idx_root]
                point_values_root = point_frame_reorder[point_key_root]

                point_key_tmp, point_other_tmp = point_key_root.split(':')
                point_other_joined = '_'.join([point_other_tmp, point_name_other])
                point_key_joined = ':'.join([point_key_tmp, point_other_joined])

                point_value_joined = {}
                for point_tag, point_data in point_fields.items():
                    if point_tag in list(point_values_root.keys()):

                        root_data = point_values_root[point_tag]

                        if isinstance(root_data, float):
                            tmp_data = [root_data, point_data]
                        elif isinstance(root_data, int):
                            tmp_data = [root_data, point_data]
                        elif isinstance(root_data, str):
                            tmp_data = [root_data, point_data]
                        elif isinstance(root_data, list):
                            tmp_data = [root_data, point_data]
                        else:
                            log_stream.warning(
                                ' ===> Type of key "' + point_tag +
                                '" is not implemented yet for dam merged object')

                        point_value_joined[point_tag] = tmp_data
                    else:
                        point_value_joined[point_tag] = point_data

                point_frame_reorder[point_key_joined] = point_value_joined
                point_frame_reorder.pop(point_key_root)

        point_frame = deepcopy(point_frame_reorder)

    return point_frame
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file point intake(s)
def read_data_point_intake(file_name, line_delimiter='#'):

    file_handle = open(file_name, 'r')
    file_lines = file_handle.readlines()
    file_handle.close()

    row_id = 0
    catch_n = int(file_lines[row_id].split(line_delimiter)[0])
    row_id += 1
    release_n = int(file_lines[row_id].split(line_delimiter)[0])

    if release_n > 0:

        point_frame = OrderedDict()
        for release_id in range(0, release_n):
            row_id += 1
            _ = parse_row2string(file_lines[row_id], line_delimiter)
            row_id += 1
            release_name = parse_row2string(file_lines[row_id], line_delimiter)
            row_id += 1
            release_idx_ji = list(map(int, parse_row2string(file_lines[row_id], line_delimiter).split()))
            row_id += 1
            release_catch_n = int(parse_row2string(file_lines[row_id], line_delimiter))

            for catch_id in range(0, int(release_catch_n)):
                row_id += 1
                catch_name = parse_row2string(file_lines[row_id], line_delimiter)
                row_id += 1
                catch_tc = int(parse_row2string(file_lines[row_id], line_delimiter))
                row_id += 1
                catch_idx_ji = list(map(int, parse_row2string(file_lines[row_id], line_delimiter).split()))
                row_id += 1
                catch_discharge_max = float(parse_row2string(file_lines[row_id], line_delimiter))
                row_id += 1
                catch_discharge_min = float(parse_row2string(file_lines[row_id], line_delimiter))
                row_id += 1
                catch_discharge_weight = float(parse_row2string(file_lines[row_id], line_delimiter))

                release_key = ':'.join([release_name, catch_name])

                point_frame[release_key] = {}
                point_frame[release_key]['release_name'] = release_name
                point_frame[release_key]['release_idx_ji'] = release_idx_ji
                point_frame[release_key]['release_catch_n'] = release_catch_n
                point_frame[release_key]['catch_name'] = catch_name
                point_frame[release_key]['catch_idx_ji'] = catch_idx_ji
                point_frame[release_key]['catch_tc'] = catch_tc
                point_frame[release_key]['catch_discharge_max'] = catch_discharge_max
                point_frame[release_key]['catch_discharge_min'] = catch_discharge_min
                point_frame[release_key]['catch_discharge_weight'] = catch_discharge_weight

    else:

        log_stream.warning(' ===> File info for intakes was found; intakes are equal to zero. Datasets is None')
        log_stream.warning(' ===> Filename ' + os.path.split(file_name)[1])
        point_frame = None

    return point_frame
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file point joint(s)
def read_data_point_joint(file_name, line_delimiter='#'):

    file_handle = open(file_name, 'r')
    file_lines = file_handle.readlines()
    file_handle.close()

    row_id = 0
    joint_n = int(file_lines[row_id].split(line_delimiter)[0])

    if joint_n > 0:
        log_stream.error(' ===> File info for joints was found; function to read joints is not implemented')
        raise NotImplementedError(' ===> Method is not implemented yet')
    else:
        log_stream.warning(' ===> File info for joints was found; joints are equal to zero. Datasets is None')
        log_stream.warning(' ===> Filename ' + os.path.split(file_name)[1])
        point_frame = None

    return point_frame

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file point lake(s)
def read_data_point_lake(file_name, line_delimiter='#'):

    file_handle = open(file_name, 'r')
    file_lines = file_handle.readlines()
    file_handle.close()

    row_id = 0
    lake_n = int(file_lines[row_id].split(line_delimiter)[0])

    if lake_n > 0:

        point_frame = OrderedDict()
        for lake_id in range(0, lake_n):
            row_id += 1
            _ = parse_row2string(file_lines[row_id], line_delimiter)
            row_id += 1
            lake_name = parse_row2string(file_lines[row_id], line_delimiter)
            row_id += 1
            lake_idx_ji = list(map(int, parse_row2string(file_lines[row_id], line_delimiter).split()))
            row_id += 1
            lake_cell_code = int(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            lake_volume_min = float(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            lake_volume_init = float(parse_row2string(file_lines[row_id], line_delimiter))
            row_id += 1
            lake_const_draining = float(parse_row2string(file_lines[row_id], line_delimiter))

            lake_key = lake_name

            point_frame[lake_key] = {}
            point_frame[lake_key]['lake_name'] = lake_name
            point_frame[lake_key]['lake_idx_ji'] = lake_idx_ji
            point_frame[lake_key]['lake_cell_code'] = lake_cell_code
            point_frame[lake_key]['lake_volume_min'] = lake_volume_min
            point_frame[lake_key]['lake_volume_init'] = lake_volume_init
            point_frame[lake_key]['lake_constant_draining'] = lake_const_draining

    else:

        log_stream.warning(' ===> File info for lakes was found; lakes are equal to zero. Datasets is None')
        log_stream.warning(' ===> Filename ' + os.path.split(file_name)[1])
        point_frame = None

    return point_frame
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write an empty data point file
def write_data_point_undefined(file_path, element_n=2, element_init=0):

    if not os.path.exists(file_path):

        element_list = [str(element_init)] * element_n

        folder_name, file_name = os.path.split(file_path)
        create_folder(folder_name)

        file_handle = open(file_path, 'w')
        for element_step in element_list:
            element_step = element_step + '\n'
            file_handle.write(element_step)
        file_handle.close()

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write an ascii grid file
def write_data_grid(file_name, file_data, file_ancillary=None):

    if 'bb_left' in list(file_ancillary.keys()):
        bb_left = file_ancillary['bb_left']
    else:
        log_stream.error(' ===> Geographical info "bb_left" for writing ascii grid file is undefined.')
        raise IOError('Geographical info is mandatory. Check your static datasets.')
    if 'bb_bottom' in list(file_ancillary.keys()):
        bb_bottom = file_ancillary['bb_bottom']
    else:
        log_stream.error(' ===> Geographical info "bb_bottom" for writing ascii grid file is undefined.')
        raise IOError('Geographical info is mandatory. Check your static datasets.')
    if 'res_lon' in list(file_ancillary.keys()):
        res_lon = file_ancillary['res_lon']
    else:
        log_stream.error(' ===> Geographical info "res_lon" for writing ascii grid file is undefined.')
        raise IOError('Geographical info is mandatory. Check your static datasets.')
    if 'res_lat' in list(file_ancillary.keys()):
        res_lat = file_ancillary['res_lat']
    else:
        log_stream.error(' ===> Geographical info "res_lat" for writing ascii grid file is undefined.')
        raise IOError('Geographical info is mandatory. Check your static datasets.')
    if 'transform' in list(file_ancillary.keys()):
        transform = file_ancillary['transform']
    else:
        log_stream.error(' ===> Geographical info "transform" for writing ascii grid file is undefined.')
        raise IOError('Geographical info is mandatory. Check your static datasets.')
    if 'no_data' in list(file_ancillary.keys()):
        no_data = file_ancillary['no_data']
    else:
        no_data = -9999
    if 'espg' in list(file_ancillary.keys()):
        epsg = file_ancillary['epsg']
    else:
        epsg = proj_epsg_default
    if 'decimal_precision' in list(file_ancillary.keys()):
        decimal_precision = int(file_ancillary['decimal_precision'])
    else:
        decimal_num = Decimal(str(file_data[0][0]))
        decimal_precision = abs(decimal_num.as_tuple().exponent)

    if isinstance(epsg, int):
        crs = CRS.from_epsg(epsg)
    elif isinstance(epsg, str):
        crs = CRS.from_string(epsg)
    else:
        log_stream.error(' ===> Geographical info "epsg" defined by using an unsupported format.')
        raise IOError('Geographical EPSG must be in string format "EPSG:4326" or integer format "4326".')

    dset_meta = dict(driver='AAIGrid', height=file_data.shape[0], width=file_data.shape[1], crs=crs,
                     count=1, dtype=str(file_data.dtype), transform=transform, nodata=no_data,
                     decimal_precision=decimal_precision)

    with rasterio.open(file_name, 'w', **dset_meta) as dset_handle:
        dset_handle.write(file_data, 1)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read an ascii grid file
def read_data_grid(file_name, output_format='data_array', output_dtype='float32'):

    try:
        dset = rasterio.open(file_name)
        bounds = dset.bounds
        res = dset.res
        transform = dset.transform
        data = dset.read()

        if dset.crs is None:
            crs = CRS.from_string(proj_epsg_default)
        else:
            crs = dset.crs

        values = data[0, :, :]

        decimal_round = 7

        center_right = bounds.right - (res[0] / 2)
        center_left = bounds.left + (res[0] / 2)
        center_top = bounds.top - (res[1] / 2)
        center_bottom = bounds.bottom + (res[1] / 2)

        lon = np.arange(center_left, center_right + np.abs(res[0] / 2), np.abs(res[0]), float)
        lat = np.arange(center_bottom, center_top + np.abs(res[0] / 2), np.abs(res[1]), float)
        lons, lats = np.meshgrid(lon, lat)

        min_lon_round = round(np.min(lons), decimal_round)
        max_lon_round = round(np.max(lons), decimal_round)
        min_lat_round = round(np.min(lats), decimal_round)
        max_lat_round = round(np.max(lats), decimal_round)

        center_right_round = round(center_right, decimal_round)
        center_left_round = round(center_left, decimal_round)
        center_bottom_round = round(center_bottom, decimal_round)
        center_top_round = round(center_top, decimal_round)

        assert min_lon_round == center_left_round
        assert max_lon_round == center_right_round
        assert min_lat_round == center_bottom_round
        assert max_lat_round == center_top_round

        lats = np.flipud(lats)

        if output_format == 'data_array':

            data_obj = create_darray_2d(values, lons, lats,
                                        coord_name_x='west_east', coord_name_y='south_north',
                                        dim_name_x='west_east', dim_name_y='south_north')

        elif output_format == 'dictionary':

            data_obj = {'values': values, 'longitude': lons, 'latitude': lats,
                        'transform': transform, 'crs': crs,
                        'bbox': [bounds.left, bounds.bottom, bounds.right, bounds.top],
                        'bb_left': bounds.left, 'bb_right': bounds.right,
                        'bb_top': bounds.top, 'bb_bottom': bounds.bottom,
                        'res_lon': res[0], 'res_lat': res[1]}
        else:
            log_stream.error(' ===> File static "' + file_name + '" output format not allowed')
            raise NotImplementedError('Case not implemented yet')

    except IOError as io_error:

        data_obj = None
        log_stream.warning(' ===> File static in ascii grid was not correctly open with error "' + str(io_error) + '"')
        log_stream.warning(' ===> Filename "' + os.path.split(file_name)[1] + '"')

    return data_obj
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to load an ascii vector file
def read_data_vector(file_name):

    file_handle = open(file_name, 'r')
    file_lines = file_handle.readlines()
    file_handle.close()

    vector_frame = [float(elem.strip('\n')) for elem in file_lines]

    return vector_frame

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read a raster ascii file
def read_data_raster(filename_reference):

    dset = rasterio.open(filename_reference)
    bounds = dset.bounds
    res = dset.res
    transform = dset.transform
    data = dset.read()
    values = data[0, :, :]

    decimal_round = 7

    center_right = bounds.right - (res[0] / 2)
    center_left = bounds.left + (res[0] / 2)
    center_top = bounds.top - (res[1] / 2)
    center_bottom = bounds.bottom + (res[1] / 2)

    lon = np.arange(center_left, center_right + np.abs(res[0] / 2), np.abs(res[0]), float)
    lat = np.arange(center_bottom, center_top + np.abs(res[0] / 2), np.abs(res[1]), float)
    lons, lats = np.meshgrid(lon, lat)

    min_lon_round = round(np.min(lons), decimal_round)
    max_lon_round = round(np.max(lons), decimal_round)
    min_lat_round = round(np.min(lats), decimal_round)
    max_lat_round = round(np.max(lats), decimal_round)

    center_right_round = round(center_right, decimal_round)
    center_left_round = round(center_left, decimal_round)
    center_bottom_round = round(center_bottom, decimal_round)
    center_top_round = round(center_top, decimal_round)

    assert min_lon_round == center_left_round
    assert max_lon_round == center_right_round
    assert min_lat_round == center_bottom_round
    assert max_lat_round == center_top_round

    lats = np.flipud(lats)

    obj = {'values': values, 'longitude': lons, 'latitude': lats,
           'transform': transform, 'bbox': [bounds.left, bounds.bottom, bounds.right, bounds.top],
           'bb_left': bounds.left, 'bb_right': bounds.right,
           'bb_top': bounds.top, 'bb_bottom': bounds.bottom,
           'res_lon': res[0], 'res_lat': res[1]}

    return obj
# -------------------------------------------------------------------------------------
