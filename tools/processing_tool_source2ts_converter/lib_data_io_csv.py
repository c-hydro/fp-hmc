"""
Library Features:

Name:          lib_data_io_csv
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20231010'
Version:       '1.0.0'
"""

# ----------------------------------------------------------------------------------------------------------------------
# libraries
import logging
import numpy as np

from lib_info_args import logger_name

# logging
log_stream = logging.getLogger(logger_name)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to write file csv
def write_file_csv(file_name, file_dframe,
                   dframe_sep=',', dframe_decimal='.', dframe_float_format='%.2f',
                   dframe_index=False, dframe_header=True,
                   dframe_index_order='ascending',
                   dframe_index_label='time', dframe_index_format='%Y-%m-%d %H:%M',
                   dframe_no_data=-9999):

    if np.isfinite(dframe_no_data):
        file_dframe.fillna(dframe_no_data, inplace=True)

    if dframe_index_format is not None:
        file_dframe.index = file_dframe.index.strftime(dframe_index_format)

    if dframe_index_order == 'ascending':
        file_dframe.sort_index(ascending=True, inplace=True)
    elif dframe_index_order == 'descending':
        file_dframe.sort_index(ascending=False, inplace=True)
    else:
        log_stream.error(' ===> Index order "' + dframe_index_order + '" is not expected by the function')
        raise NotImplementedError('Index order is not correctly defined [ascending, descending]')

    file_dframe.to_csv(
        file_name, mode='w',
        index=dframe_index, sep=dframe_sep, decimal=dframe_decimal,
        index_label=dframe_index_label,
        header=dframe_header, float_format=dframe_float_format,  quotechar='"')

# ----------------------------------------------------------------------------------------------------------------------
