"""
Class Features

Name:          lib_data_geo_shapefile
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20201122'
Version:       '1.0.0'
"""

#######################################################################################
# Libraries
import logging
import geopandas as gpd
import numpy as np

from copy import deepcopy

import pandas as pd

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to read shapefile section(s)
def read_data_shapefile_section(file_name, columns_name_expected=None, columns_name_defined=None,
                                columns_name_type=None, row_filter_type=None):

    if columns_name_expected is None:
        columns_name_expected = ['HMC_X', 'HMC_Y', 'BASIN', 'SEC_NAME', 'SEC_RS', 'AREA',
                                 'Q_THR1', 'Q_THR2', 'DOMAIN', 'BASEFLOW']
    if columns_name_type is None:
        columns_name_type = ['int', 'int', 'str', 'str', 'int', 'float', 'float',
                             'float', 'float', 'str', 'float']

    if columns_name_defined is None:
        columns_name_defined = ['section_idx_j', 'section_idx_i',
                                'section_domain', 'section_name', 'section_code',
                                'section_drained_area', 'section_discharge_thr_alert', 'section_discharge_thr_alarm',
                                'section_reference', 'section_baseflow']

    file_dframe_raw = gpd.read_file(file_name)
    file_rows = file_dframe_raw.shape[0]

    if 'BASEFLOW' not in list(file_dframe_raw.columns):
        file_dframe_raw['BASEFLOW'] = 0.0

    if (row_filter_type is not None) and (isinstance(row_filter_type, dict)):
        for row_filter_key, row_filter_value in row_filter_type.items():
            if (row_filter_key is not None) and (row_filter_value is not None):
                if isinstance(row_filter_value, str):
                    file_dframe_raw_tmp = file_dframe_raw.loc[
                        file_dframe_raw[row_filter_key].str.lower() == row_filter_value.lower()]
                else:
                    log_stream.error(' ===> Datatype for filtering columns is not allowed')
                    raise NotImplementedError('Datatype not implemented yet')

                file_dframe_raw = deepcopy(file_dframe_raw_tmp)

    if isinstance(file_dframe_raw, pd.DataFrame):
        if file_dframe_raw.empty:
            log_stream.error(' ===> The section object should not be empty')
            raise IOError('Check your shapefile or filters type to solve this issue')
    else:
        log_stream.error(' ===> The section object must be a dataframe')
        raise RuntimeError('Unexpected error')

    file_obj = {}
    type_obj = {}
    for column_name_exp, column_type, column_name_def in zip(
            columns_name_expected, columns_name_type, columns_name_defined):

        if column_name_exp in file_dframe_raw.columns:
            column_data = file_dframe_raw[column_name_exp].values.tolist()
        else:

            log_stream.warning(' ===> Column ' + column_name_exp +
                               ' not available in shapefile. Initialized with undefined values according with datatype')
            if column_type == 'int':
                column_data = [-9999] * file_rows
            elif column_type == 'str':
                column_data = [''] * file_rows
            elif column_type == 'float':
                column_data = [-9999.0] * file_rows
            else:
                log_stream.error(' ===> Datatype for undefined columns in the section shapefile is not allowed')
                raise NotImplementedError('Datatype not implemented yet')

        type_data_alpha = []
        type_data_numeric = []
        for step_data in column_data:
            if isinstance(step_data, str):
                if step_data.isalpha():
                    type_data_alpha.append(True)
                    type_data_numeric.append(False)
                elif step_data.isnumeric():
                    type_data_alpha.append(False)
                    type_data_numeric.append(True)
            elif isinstance(step_data, (int, float)):
                type_data_alpha.append(False)
                type_data_numeric.append(True)

        if all(type_data_alpha):
            type_data = 'str'
            no_data = 'NA'
        elif all(type_data_numeric):
            type_data = 'numeric'
            no_data = -9999.0
        else:
            log_stream.error(' ===> Datatype of the columns "' + column_name_exp +
                             '"  must be character or numeric. Mixed mode is not allowed')
            raise NotImplementedError('Datatype not implemented yet')

        column_data_def = []
        for column_step in column_data:
            if column_step is None:
                column_data_def.append(no_data)
            else:
                column_data_def.append(column_step)
        else:
            column_data_def = column_data

        file_obj[column_name_def] = column_data_def
        type_obj[column_name_def] = type_data

    file_points = convert_obj_list2point(file_obj, file_pivot_order=['section_domain', 'section_name'])

    return file_points
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert section obj list to section obj point
def convert_obj_list2point(file_obj, file_pivot_order=None, file_pivot_sep=':'):

    if file_pivot_order is None:
        file_pivot_order = ['section_domain', 'section_name']

    file_pivot_obj_element = None
    file_pivot_lists = []
    for file_pivot_step in file_pivot_order:
        if file_pivot_step in list(file_obj.keys()):
            file_pivot_list = file_obj[file_pivot_step]
            if file_pivot_obj_element is None:
                file_pivot_obj_element = file_pivot_list.__len__()
            file_pivot_lists.append(file_pivot_list)
        else:
            log_stream.error(' ===> File pivot ' + file_pivot_step + ' is not in the section shapefile.')
            raise IOError('Check your section shapefile to find the correct pivot name')

    file_pivot_points = {}
    for file_pivot_list in [file_pivot_lists[0]]:
        for id_element, file_element in enumerate(file_pivot_list):

            tag_element = []
            for file_pivot_tmp in file_pivot_lists:
                tag_element.append(file_pivot_tmp[id_element])
            tag_str = file_pivot_sep.join(tag_element)

            file_pivot_points[tag_str] = {}
            for file_key, file_fields in file_obj.items():
                file_value = file_fields[id_element]
                file_pivot_points[tag_str][file_key] = {}
                file_pivot_points[tag_str][file_key] = file_value

    return file_pivot_points

# -------------------------------------------------------------------------------------
