"""
Class Features

Name:          lib_data_geo_shapefile
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210113'
Version:       '1.0.0'
"""

#######################################################################################
# Libraries
import logging
import pandas as pd
import geopandas as gpd

from copy import deepcopy

# Log
log_stream = logging.getLogger(__name__)
log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)-80s %(filename)s:[%(lineno)-6s - %(funcName)-20s()] '
logging.basicConfig(level=logging.DEBUG, format=log_format)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to find data section
def find_data_section(section_df, section_name=None, basin_name=None,
                      tag_column_section_in='section_name', tag_column_basin_in='section_domain',
                      tag_column_section_out='section_name', tag_column_basin_out='basin_name'):

    section_name_ref = section_name.lower()
    basin_name_ref = basin_name.lower()

    section_name_list = section_df[tag_column_section_in].values
    basin_name_list = section_df[tag_column_basin_in].values

    section_dict_tmp = {tag_column_section_in: section_name_list, tag_column_basin_in: basin_name_list}
    section_df_tmp = pd.DataFrame(data=section_dict_tmp)
    section_df_tmp = section_df_tmp.astype(str).apply(lambda x: x.str.lower())

    point_idx = section_df_tmp[(section_df_tmp[tag_column_section_in] == section_name_ref) &
                                 (section_df_tmp[tag_column_basin_in] == basin_name_ref)].index

    if point_idx.shape[0] == 1:
        point_idx = point_idx[0]
        point_dict = section_df.iloc[point_idx, :].to_dict()

        point_dict[tag_column_section_out] = point_dict.pop(tag_column_section_in)
        point_dict[tag_column_basin_out] = point_dict.pop(tag_column_basin_in)

    elif point_idx.shape[0] == 0:
        log_stream.error(' ===> Section idx not found in the section dictionary.')
        raise IOError('Section selection failed; section not found')
    else:
        log_stream.error(' ===> Section idx not found. Procedure will be exit for unexpected error.')
        raise NotImplementedError('Section selection failed for unknown reason.')

    return point_dict
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to filter data section
def filter_data_section(dframe_obj, filter_column='section_type', filter_value='River'):

    if filter_column in list(dframe_obj.columns):
        if filter_value is not None:
            dframe_selection = dframe_obj.loc[dframe_obj[filter_column] == filter_value]
        else:
            dframe_selection = deepcopy(dframe_obj)
        dframe_selection.attrs = {'filter_column': filter_column, 'filter_value': filter_value}
    else:
        log_stream.error(' ===> Column name "' + filter_column + '" to filter dataframe not found')
        raise IOError('Check your shapefile and your "filter_column" option')

    if dframe_selection.empty:
        log_stream.error(' ===> Column value "' +
                         str(filter_value) + '" to filter dataframe not found. Empty dataframe was selected.')
        raise IOError('Check your shapefile and your "filter_value" options')

    return dframe_selection


# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read shapefile section(s)
def read_data_section(file_name, columns_name_expected_in=None, columns_name_expected_out=None, columns_name_type=None):

    if columns_name_expected_in is None:
        columns_name_expected_in = [
            'HMC_X', 'HMC_Y', 'LAT', 'LON', 'BASIN', 'SEC_NAME', 'SEC_RS', 'AREA', 'Q_THR1', 'Q_THR2', 'TYPE']

    if columns_name_expected_out is None:
        columns_name_expected_out = [
            'hmc_idx_x', 'hmc_idx_y', 'latitude', 'longitude', 'section_domain', 'section_name', 'section_code',
            'section_drained_area', 'section_discharge_thr_alert', 'section_discharge_thr_alarm', 'section_type']

    if columns_name_type is None:
        columns_name_type = ['int', 'int', 'float', 'float',
                             'str', 'str', 'float', 'float', 'float', 'float',
                             'str']

    file_dframe_raw = gpd.read_file(file_name)
    file_rows = file_dframe_raw.shape[0]

    section_obj = {}
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
                log_stream.error(' ===> Column Datatype is not allowed.')
                raise NotImplementedError('Datatype not implemented yet')

        section_obj[column_name_out] = column_data

    section_df = pd.DataFrame(data=section_obj)

    return section_df
# -------------------------------------------------------------------------------------
