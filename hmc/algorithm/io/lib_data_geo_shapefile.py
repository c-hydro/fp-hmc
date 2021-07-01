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

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to read shapefile section(s)
def read_data_shapefile_section(file_name, columns_name_expected=None, columns_name_type=None):

    if columns_name_expected is None:
        columns_name_expected = ['HMC_X', 'HMC_Y', 'BASIN', 'SEC_NAME', 'SEC_RS', 'AREA', 'Q_THR1', 'Q_THR2']
    if columns_name_type is None:
        columns_name_type = ['int', 'int', 'str', 'str', 'int', 'float', 'float', 'float']

    file_dframe_raw = gpd.read_file(file_name)
    file_rows = file_dframe_raw.shape[0]

    file_obj = {}
    type_obj = {}
    for column_name, column_type in zip(columns_name_expected, columns_name_type):
        if column_name in file_dframe_raw.columns:
            column_data = file_dframe_raw[column_name].values.tolist()
        else:

            log_stream.warning(' ===> Column ' + column_name +
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
            log_stream.error(' ===> Datatype of the columns "' + column_name +
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

        file_obj[column_name] = column_data_def
        type_obj[column_name] = type_data

    return file_obj
# -------------------------------------------------------------------------------------
