"""
Library Features:

Name:          lib_data_io_generic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20240222'
Version:       '1.0.0'
"""
# ----------------------------------------------------------------------------------------------------------------------
# libraries
import logging

import numpy as np
import pandas as pd

from copy import deepcopy

from lib_info_args import logger_name, time_format_algorithm

# logging
log_stream = logging.getLogger(logger_name)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to select data point
def extract_data_point(var_time, var_da, grid_obj, point_obj, var_name='discharge'):

    # define time string
    str_time = var_time.strftime(time_format_algorithm)

    # organize data point
    point_name_arr = point_obj['name'].values
    point_idx_x_arr, point_idx_y_arr = point_obj['idx_x'].values, point_obj['idx_y'].values
    # extract check point
    grid_obj_point_arr = grid_obj[point_idx_y_arr, point_idx_x_arr]

    # check data grid
    if var_da is not None:
        # organize data grid
        var_obj = var_da.values.squeeze()
        # extract data point
        var_obj_point_arr = var_obj[point_idx_y_arr, point_idx_x_arr]
    else:
        # organize data grid (no data case)
        var_obj_point_arr = np.zeros([len(point_obj), 1]) * np.nan
        log_stream.warning(' ===> Data grid is empty for the selected time step "' + str_time + '"')

    # organize point data
    point_data = {}
    for point_i, point_name_step in enumerate(point_name_arr):

        grid_obj_point_i = grid_obj_point_arr[point_i]
        var_obj_point_i = var_obj_point_arr[point_i]

        if var_name == 'discharge':
            if grid_obj_point_i == 0:
                var_obj_point_i = np.nan

        point_data[point_name_step] = var_obj_point_i

    # organize dframe point
    point_df = pd.DataFrame(data=point_data, index=[var_time])

    return point_df
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to combine data point
def combine_data_point(point_df_step, point_df_combined=None):

    if point_df_combined is None:
        point_df_combined = deepcopy(point_df_step)
    else:
        point_df_combined = point_df_combined.append(point_df_step)

    return point_df_combined


# ----------------------------------------------------------------------------------------------------------------------
