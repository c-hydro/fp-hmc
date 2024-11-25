"""
Class Features

Name:          lib_data_io_shapefile
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210730'
Version:       '1.0.1'
"""

#######################################################################################
# Libraries
import logging

import pandas as pd
import geopandas as gpd

logging.getLogger('fiona').setLevel(logging.WARNING)
logging.getLogger('geopandas').setLevel(logging.WARNING)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to find point data
def find_data_point(point_df, point_name=None, basin_name=None,
                    tag_column_point_in='point_name', tag_column_basin_in='point_domain',
                    tag_column_point_out='point_name', tag_column_basin_out='basin_name'):

    point_name_ref = point_name.lower()
    basin_name_ref = basin_name.lower()

    point_name_list = point_df[tag_column_point_in].values
    basin_name_list = point_df[tag_column_basin_in].values

    point_dict_tmp = {tag_column_point_in: point_name_list, tag_column_basin_in: basin_name_list}
    point_df_tmp = pd.DataFrame(data=point_dict_tmp)
    point_df_tmp = point_df_tmp.astype(str).apply(lambda x: x.str.lower())

    point_idx = point_df_tmp[(point_df_tmp[tag_column_point_in] == point_name_ref) &
                             (point_df_tmp[tag_column_basin_in] == basin_name_ref)].index

    if point_idx.shape[0] == 1:
        point_idx = point_idx[0]
        point_dict = point_df.iloc[point_idx, :].to_dict()

        point_dict[tag_column_point_out] = point_dict.pop(tag_column_point_in)
        point_dict[tag_column_basin_out] = point_dict.pop(tag_column_basin_in)

    elif point_idx.shape[0] == 0:
        raise IOError('Point selection failed; point not found')
    else:
        raise NotImplementedError('Point selection failed for unknown reason.')

    return point_dict
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read dam(s) data (shapefile)
def read_data_dam(file_name, columns_name_expected_in=None, columns_name_expected_out=None, columns_name_type=None):

    if columns_name_expected_in is None:
        columns_name_expected_in = [
            'HMC_X', 'HMC_Y', 'LAT', 'LON', 'BASIN', 'NAME', 'STATION', 'AREA', 'Q_THR1', 'Q_THR2']

    if columns_name_expected_out is None:
        columns_name_expected_out = [
            'hmc_idx_x', 'hmc_idx_y', 'latitude', 'longitude', 'point_domain', 'point_name', 'point_code',
            'point_drained_area', 'point_discharge_thr_alert', 'point_discharge_thr_alarm']

    if columns_name_type is None:
        columns_name_type = ['int', 'int', 'float', 'float',
                             'str', 'str', 'str', 'float', 'float', 'float']

    file_dframe_raw = gpd.read_file(file_name)
    file_rows = file_dframe_raw.shape[0]

    point_obj = {}
    for column_name_in, column_name_out, column_type in zip(columns_name_expected_in,
                                                            columns_name_expected_out, columns_name_type):
        if column_name_in in file_dframe_raw.columns:
            column_data = file_dframe_raw[column_name_in].values.tolist()
        else:
            if column_type == 'int':
                column_data = [-9999] * file_rows
            elif column_type == 'str':
                column_data = [''] * file_rows
            elif column_type == 'float':
                column_data = [-9999.0] * file_rows
            else:
                raise NotImplementedError('Datatype not implemented yet')

        point_obj[column_name_out] = column_data

    point_df = pd.DataFrame(data=point_obj)

    return point_df
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read section(s) data (shapefile)
def read_data_section(file_name, columns_name_expected_in=None, columns_name_expected_out=None, columns_name_type=None):

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
            column_data = file_dframe_raw[column_name_in].values.tolist()
        else:
            if column_type == 'int':
                column_data = [-9999] * file_rows
            elif column_type == 'str':
                column_data = [''] * file_rows
            elif column_type == 'float':
                column_data = [-9999.0] * file_rows
            else:
                raise NotImplementedError('Datatype not implemented yet')

        point_obj[column_name_out] = column_data

    point_df = pd.DataFrame(data=point_obj)

    return point_df
# -------------------------------------------------------------------------------------