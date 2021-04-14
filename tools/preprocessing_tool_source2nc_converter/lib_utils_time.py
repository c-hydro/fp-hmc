"""
Library Features:

Name:          lib_utils_time
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Libraries
import logging
import pandas as pd

from tools.preprocessing_tool_source2nc_converter.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to set time run
def set_time(time_start=None, time_end=None, time_format='%Y-%m-%d %H:$M',
             time_period=None, time_frequency='H', time_rounding='H', time_reverse=False):

    log_stream.info(' ---> Set time range ... ')

    if time_start is not None:
        time_start = pd.Timestamp(time_start)
        time_start = time_start.floor(time_rounding)
    if time_end is not None:
        time_end = pd.Timestamp(time_end)
        time_end = time_end.floor(time_rounding)

    if (time_start is not None) and (time_end is not None):
        time_range = pd.date_range(start=time_start, end=time_end, freq=time_frequency)
    else:
        logger_name.info(' ---> Set time range ... FAILED')
        logger_name.error(' ===> Time options are not correctly set')
        raise NotImplementedError('Case not implemented yet')

    if time_reverse:
        time_range = time_range[::-1]

    time_chunks = set_chunks(time_range)

    log_stream.info(' ---> Set time range ... DONE')

    return time_chunks, time_range

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to set chunks
def set_chunks(time_range, time_period='D'):

    time_groups = time_range.to_period(time_period)
    time_chunks = time_range.groupby(time_groups)

    return time_chunks
# -------------------------------------------------------------------------------------
