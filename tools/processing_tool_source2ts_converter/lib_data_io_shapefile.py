"""
Library Features:

Name:          lib_data_io_shapefile
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20240222'
Version:       '1.0.0'
"""
# ----------------------------------------------------------------------------------------------------------------------
# libraries
import logging

import numpy as np
import pandas as pd
import geopandas as gpd

from lib_info_args import logger_name

# logging
log_stream = logging.getLogger(logger_name)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to select data point
def select_data_point(dframe_point, tag_name='DomainContinuum', tag_value=None):
    dframe_point_selected = None
    if tag_value is not None:
        dframe_point_selected = dframe_point[dframe_point[tag_name] == tag_value]
    return dframe_point_selected
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to read shapefile point
def read_data_point(file_name, columns_name_expected_in=None, columns_name_expected_out=None, columns_name_type=None):

    if columns_name_expected_in is None:
        columns_name_expected_in = [
            'DOMAIN', 'DOMAIN_DES', 'BASIN',
            'SEC_CODE', 'SEC_NAME', 'SEC_DES', 'SEC_RS', 'SEC_TAG',
            'TYPE',
            'HMC_X', 'HMC_Y', 'LAT', 'LON', 'AREA',
            'Q_THR1', 'Q_THR2', 'Q_THR3']

    if columns_name_expected_out is None:
        columns_name_expected_out = [
            'point_domain_name', 'point_domain_description', 'point_catchment_name',
            'point_code_ws', 'point_section_name', 'point_catchment_description', 'point_code_rs', 'point_tag',
            'point_type',
            'point_idx_x_hmc', 'point_idx_y_hmc',  'latitude', 'longitude', 'area',
            'point_discharge_thr1', 'point_discharge_thr2', 'point_discharge_thr3']

    if columns_name_type is None:
        columns_name_type = [
            'str', 'str', 'str',
            'str', 'str', 'str', 'str', 'str',
            'int', 'int', 'float', 'float', 'float'
            'float', 'float', 'float']

    file_dframe_raw = gpd.read_file(file_name)
    file_rows = file_dframe_raw.shape[0]

    point_obj = {}
    for column_name_in, column_name_out, column_type in zip(columns_name_expected_in,
                                                            columns_name_expected_out, columns_name_type):

        if column_name_in in file_dframe_raw.columns:

            column_data_tmp = file_dframe_raw[column_name_in].values.tolist()

            if column_type == 'int':
                column_data_def = np.array(column_data_tmp, dtype=int)
            elif column_type == 'str' or column_type == 'string':
                column_data_def = np.array(column_data_tmp, dtype=str)
            elif column_type == 'float':
                column_data_def = np.array(column_data_tmp, dtype=float)
            else:
                log_stream.error(' ===> Column name "' + column_name_in + '" has not an expected datatype format')
                raise NotImplementedError('Datatype not implemented yet')

        else:
            if column_type == 'int':
                column_data_def = [-9999] * file_rows
            elif column_type == 'str' or column_type == 'string':
                column_data_def = [''] * file_rows
            elif column_type == 'float':
                column_data_def = [-9999.0] * file_rows
            else:
                log_stream.error(' ===> Column name "' + column_name_in + '" has not an expected datatype format')
                raise NotImplementedError('Datatype not implemented yet')

        point_obj[column_name_out] = column_data_def

    point_df = pd.DataFrame(data=point_obj)

    return point_df
# ----------------------------------------------------------------------------------------------------------------------
