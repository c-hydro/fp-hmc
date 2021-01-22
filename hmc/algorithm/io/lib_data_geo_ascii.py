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

from collections import OrderedDict

from hmc.algorithm.io.lib_data_io_generic import create_darray_2d

from hmc.algorithm.utils.lib_utils_system import create_folder
from hmc.algorithm.utils.lib_utils_list import pad_or_truncate_list
from hmc.algorithm.utils.lib_utils_string import parse_row2string
from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to write file point section(s)
def write_data_point_section(file_name, file_data, file_cols_expected=8):

    file_keys = list(file_data.keys())

    cols = file_data.__len__()
    if cols != file_cols_expected:
        log_stream.error(' ===> File sections columns ' + str(cols) + ' found != columns expected' +
                         str(file_cols_expected))
        raise IOError('File datasets are in a wrong format')

    rows = -9999
    for key in file_keys:
        if rows != file_data[key].__len__():
            rows = file_data[key].__len__()
            break

    file_obj = []
    for i in range(0, rows):
        row = []
        for key in file_keys:
            point = file_data[key][i]
            row.append(point)
        file_obj.append(row)

    file_folder = os.path.split(file_name)[0]
    create_folder(file_folder)
    with open(file_name, "w", encoding='utf-8') as file:
        for file_row in file_obj:
            string_row = ' '.join(str(item) for item in file_row)
            string_row = string_row + '\n'
            file.write(string_row)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read file point section(s)
def read_data_point_section(file_name, section_cols_expected=8):

    file_handle = open(file_name, 'r')
    file_lines = file_handle.readlines()
    file_handle.close()

    point_frame = OrderedDict()
    for row_id, row_data in enumerate(file_lines):
        section_row = row_data.strip()
        section_cols = section_row.split()

        if section_cols.__len__() < section_cols_expected:
            section_cols = pad_or_truncate_list(section_cols, section_cols_expected)

        section_idx_ji = [int(section_cols[0]), int(section_cols[1])]
        section_domain = section_cols[2]
        section_name = section_cols[3]
        section_code = int(section_cols[4])
        section_drained_area = float(section_cols[5])
        section_discharge_thr_alert = float(section_cols[6])
        section_discharge_thr_alarm = float(section_cols[7])
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

    point_frame = OrderedDict()
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

            if plant_name != '':
                dam_key = ':'.join([dam_name, plant_name])
            else:
                dam_key = dam_name

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

    point_frame = OrderedDict()
    for release_id in range(0, release_n):
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

    return point_frame
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to load an ascii grid file
def read_data_grid(file_name):

    try:
        dset = rasterio.open(file_name)
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

        da_frame = create_darray_2d(values, lons, lats,
                                    coord_name_x='west_east', coord_name_y='south_north',
                                    dim_name_x='west_east', dim_name_y='south_north')
    except IOError as io_error:
        da_frame = None
        log_stream.warning(' ===> File static in ascii grid was not correctly open with error ' + str(io_error))
        log_stream.warning(' ===> Filename ' + os.path.split(file_name)[1])

    return da_frame
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
