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
# Method to split time frequency string in digits and alphabetic parts
def parse_timefrequency_to_timeparts(time_fr_string):

    time_fr_digits = list(filter(str.isdigit, time_fr_string))
    if time_fr_digits.__len__() == 1:
        fr_part_digits = int(time_fr_digits[0])
    elif time_fr_digits.__len__() == 0:
        fr_part_digits = 1
    else:
        log_stream.error(' ==> Time frequency digits part is not correctly defined')
        raise NotImplementedError('Case not implemented yet')

    time_fr_alpha = list(filter(str.isalpha, time_fr_string))
    if time_fr_alpha.__len__() == 1:
        fr_part_alpha = time_fr_alpha[0]
    else:
        log_stream.error(' ==> Time frequency alphabetic part is not correctly defined')
        raise NotImplementedError('Case not implemented yet')

    return fr_part_digits, fr_part_alpha
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert timestamp to time str
def convert_timestamp_to_timestring(time_stamp, time_format='%Y-%m-%d %H:%M'):
    time_string = time_stamp.strftime(time_format)
    return time_string
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert frequency string to frequency seconds
def convert_freqstr_to_freqsecs(time_frequency_digits, time_frequency_alphabetic):
    time_frequency_string = ''.join([str(time_frequency_digits), time_frequency_alphabetic])
    time_frequency_seconds = int(pd.Timedelta(time_frequency_string).total_seconds())
    return time_frequency_seconds
# -------------------------------------------------------------------------------------
