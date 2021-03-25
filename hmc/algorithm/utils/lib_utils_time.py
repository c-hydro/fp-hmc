"""
Library Features:

Name:          lib_utils_time
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200402'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging

import pandas as pd

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to get time
def get_time(time_str, time_rounding='H'):
    time_obj_raw = pd.Timestamp(time_str)
    time_obj_round = time_obj_raw.floor(time_rounding)
    return time_obj_round
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert timestamp to time str
def convert_timestamp_to_timestring(time_stamp, time_format='%Y-%m-%d %H:%M'):
    time_string = time_stamp.strftime(time_format)
    return time_string
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert frequency string to frequency seconds
def convert_freqstr_to_freqsecs(time_frequency_string):
    if not time_frequency_string[0].isdigit():
        time_frequency_string = '1' + time_frequency_string
    time_frequency_seconds = int(pd.Timedelta(time_frequency_string).total_seconds())
    return time_frequency_seconds
# -------------------------------------------------------------------------------------
