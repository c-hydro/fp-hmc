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
        columns_name_type = ['int', 'int', 'str', 'str', 'str', 'float', 'float', 'float']

    file_dframe_raw = gpd.read_file(file_name)
    file_rows = file_dframe_raw.shape[0]

    file_obj = {}
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

        file_obj[column_name] = column_data

    return file_obj
# -------------------------------------------------------------------------------------
