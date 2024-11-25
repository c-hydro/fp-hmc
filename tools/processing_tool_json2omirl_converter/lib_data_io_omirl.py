"""
Library Features:

Name:          lib_data_io_ascii
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210730'
Version:       '1.0.1'
"""
#######################################################################################
# Library
import logging
import collections

import numpy as np
import pandas as pd

from lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to prepare time-series datasets in dewetra format
def prepare_info_dewetra(point_data,
                         tag_ts_obs='time_series_discharge_observed',
                         tag_ts_mod='time_series_discharge_simulated'):

    keys_data = list(point_data.keys())

    time_period = pd.DatetimeIndex(point_data['time_period'])
    time_from = point_data['time_start']
    time_now = point_data['time_run']

    time_freq = time_period.inferred_freq
    if isinstance(time_freq, str):
        if not time_freq[0].isdigit():
            time_freq = '1' + time_freq
    time_resolution_seconds = pd.to_timedelta(time_freq).seconds
    time_resolution_mins = time_resolution_seconds / 60

    idx_start = time_period.get_loc(time_from)

    keys_obs = tag_ts_obs
    keys_mod = []
    for key_step in keys_data:
        if tag_ts_mod in key_step:
            keys_mod.append(key_step)

    point_ts_obs = point_data[keys_obs][idx_start:].tolist()

    point_ts_mod = []
    for key_step in keys_mod:
        point_ts_tmp = point_data[key_step][idx_start:].tolist()
        point_ts_mod.append(point_ts_tmp)

    run_n = keys_mod.__len__()

    return point_ts_obs, point_ts_mod, time_now, time_from, time_resolution_mins, run_n

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write time-series datasets in dewetra format
def write_file_dewetra(file_name, file_data_obs, file_data_mod,
                       time_now, time_from, time_resolution,
                       run_n=1, run_name='hmc_ts_outcome'):

    # Save update information
    data_ws = {'line_01': 'Procedure=' + str(run_name) + ' \n',
               'line_02': 'DateMeteoModel=' + str(time_now) + ' \n',
               'line_03': 'DateStart=' + str(time_from) + ' \n',
               'line_04': 'Temp.Resolution=' + str(int(time_resolution)) + ' \n',
               'line_05': 'SscenariosNumber=' + str(int(run_n)) + ' \n',
               'line_06': (' '.join(map(str, file_data_obs))) + ' \n'}

    # Iterate over run(s)
    line_format = '{:02d}'
    for id, data_mod in enumerate(file_data_mod):
        line_str = 'line_' + line_format.format(id + 7)
        data_ws[line_str] = (' '.join(map(str, data_mod))) + ' \n'

    # Dictionary sorting
    data_ws_ord = collections.OrderedDict(sorted(data_ws.items()))

    # Open ASCII file (to save all data)
    file_handler = open(file_name, 'w')

    # Write data in ASCII file
    file_handler.writelines(data_ws_ord.values())
    # Close ASCII file
    file_handler.close()
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to read dewetra file for deterministic run
def read_file_dewetra_deterministic(file_name, header_delimiter='='):

    # Get handle
    file_handle = open(file_name, 'r')

    # Read header
    file_header = {
        "Procedure": file_handle.readline().split(header_delimiter)[1].strip(),
        "DateMeteoModel": file_handle.readline().split(header_delimiter)[1].strip(),
        "DateStart": file_handle.readline().split(header_delimiter)[1].strip(),
        "Temp.Resolution": int(file_handle.readline().split(header_delimiter)[1]),
        "SscenariosNumber": int(file_handle.readline().split(header_delimiter)[1]),
    }

    # Read data
    file_data = np.loadtxt(file_handle, skiprows=0)
    file_data_obs = file_data[0]
    file_date_mod = file_data[1]

    return file_header, file_data_obs, file_date_mod
# ----------------------------------------------------------------------------------------------------------------------
