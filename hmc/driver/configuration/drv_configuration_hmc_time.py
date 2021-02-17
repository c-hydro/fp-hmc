"""
Class Features

Name:          drv_configuration_hmc_time
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import warnings
import re

import pandas as pd
import numpy as np

from hmc.algorithm.utils.lib_utils_time import get_time, convert_timestamp_to_timestring
from hmc.algorithm.utils.lib_utils_geo import compute_corrivation_time
from hmc.algorithm.utils.lib_utils_string import separate_number_chars
from hmc.algorithm.utils.lib_utils_dataframe import convert_dict_2_df
from hmc.algorithm.default.lib_default_args import logger_name, \
    time_format_algorithm, time_format_datasets, time_calendar, time_units

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class data object
class DataObj(dict):
    pass
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Class to configure time
class ModelTime:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, time_arg, obj_time_info_ref, template_time=None, **kwargs):

        self.time_run_arg = time_arg
        self.obj_time_info_ref = obj_time_info_ref

        if self.obj_time_info_ref['time_run'] is not None:
            self.time_run_info = get_time(self.obj_time_info_ref['time_run'])
        else:
            self.time_run_info = None

        if self.time_run_arg is not None:
            self.time_run = self.time_run_arg
        else:
            self.time_run = self.time_run_info

        # Set the steps to search in forecast part the nwp availability
        self.eta_period = 0
        # Set column delimiter
        self.column_sep = ';'

        if self.time_run is None:
            log_stream.error(' ===> Time run is not defined!')
            raise IOError(' Define time run using or algorithm file settings or algorithm arguments!')

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize time
    def organize_time(self, run_obj, dset_terrain=None):

        # Starting information
        log_stream.info(' ----> Organize time information ... ')

        # Get run indexes
        run_list = list(run_obj.keys())

        # Set corrivation time
        time_tc = self.set_corrivation_time(dset_terrain)

        # Define time obj and dataframe(s)
        obj_time_info, _ = self.set_time_info(run_list, time_tc)
        obj_time_df = self.set_time_data(obj_time_info, column_sep=self.column_sep)
        obj_time_df = self.set_time_slice(obj_time_info, obj_time_df, time_type_excluded=None)

        # Ending information
        log_stream.info(' ----> Organize time information ... DONE')

        return obj_time_info, obj_time_df

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set corrivation time
    def set_corrivation_time(self, dset_terrain):

        geo_values = dset_terrain['values']
        geo_x = dset_terrain['longitude']
        geo_y = dset_terrain['latitude']
        geo_res_x = dset_terrain['res_lon']
        geo_res_y = dset_terrain['res_lat']

        time_tc_alg = self.obj_time_info_ref['time_tc']

        if time_tc_alg == -9999:
            time_tc_run = compute_corrivation_time(geo_values, geo_x, geo_y, geo_res_x, geo_res_y)
            log_stream.info(' -----> Corrivation time derived by terrain raster (tc = ' + str(time_tc_run) + ' hours)')
        else:
            time_tc_run = time_tc_alg
            log_stream.info(' -----> Corrivation time derived by user settings (tc = ' + str(time_tc_run) + ' hours)')

        if time_tc_run < 0:
            time_tc_run = 0
            log_stream.warning(' ===> Corrivation time less then 0 (tc = 0 hours')

        return time_tc_run
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to slice time series obj
    @staticmethod
    def set_time_slice(time_info, time_ts, time_subset='File_Group', time_type_excluded=None, time_type_split='CORR'):

        time_dict = {}
        for (run_tag, time_ts_step), time_info_step in zip(time_ts.items(), time_info.values()):

            time_idx_all = time_ts_step.index
            time_idx_days = time_idx_all.map(pd.Timestamp.date).unique()

            for idx_step, time_idx_step in enumerate(time_idx_days):
                time_idx_step = pd.Timestamp(time_idx_step)

                year_idx_step = time_idx_step.year
                month_idx_step = time_idx_step.month
                day_idx_step = time_idx_step.day

                time_idx_select = time_idx_all[(time_idx_all.year == year_idx_step) &
                                               (time_idx_all.month == month_idx_step) &
                                               (time_idx_all.day == day_idx_step)]

                time_ts_step.loc[time_idx_select, time_subset] = idx_step

            time_run_step = time_info_step['time_run']
            group_ts_step = int(time_ts_step.loc[time_run_step][time_subset])

            time_ts_step.loc[time_idx_all > time_run_step, time_subset] = group_ts_step + 1

            if time_type_excluded is not None:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    time_ts_step[time_subset].loc[time_ts_step['File_Type'] == time_type_excluded] = np.nan

            if time_type_split is not None:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    time_ts_step[time_subset].loc[time_ts_step['File_Type'] == time_type_split] = group_ts_step + 2

            time_dict[run_tag] = time_ts_step

        return time_dict
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute time series obj
    @staticmethod
    def set_time_data(time_obj=None,
                      time_name_index='Time', column_sep=';',
                      column_file_type='File_Type', column_file_eta='File_ETA',
                      column_exec_type='Exec_Type', column_exec_eta='Exec_ETA',
                      column_file_pre_processing='PreProc_Step', column_file_post_processing='PostProc_Step',
                      column_file_step='File_Step', column_file_check='File_Check'):

        time_dict = {}
        for run_tag, time_data in time_obj.items():

            datetime_range_idx = time_data['time_run_range']
            datetime_obs_idx = time_data['time_observed_range']
            datetime_for_idx = time_data['time_forecast_range']
            datetime_obs_eta = time_data['time_observed_eta']
            datetime_for_eta = time_data['time_forecast_eta']
            datetime_check_idx = time_data['time_check_range']
            datetime_tc_idx = time_data['time_tc_range']
            datetime_restart_idx = pd.DatetimeIndex([time_data['time_stamp_restart']])
            datetime_run_idx = pd.DatetimeIndex([time_data['time_run']])

            datetime_range_idx = datetime_range_idx.union(datetime_restart_idx)

            time_tmp = pd.DataFrame({
                time_name_index: datetime_range_idx,
                column_file_type: ['NA'] * datetime_range_idx.__len__(),
                column_file_pre_processing: ['NA'] * datetime_range_idx.__len__(),
                column_file_post_processing: ['NA'] * datetime_range_idx.__len__(),
                column_file_eta: ['NA'] * datetime_range_idx.__len__(),
                column_exec_type: ['NA'] * datetime_range_idx.__len__(),
                column_exec_eta: ['NA'] * datetime_range_idx.__len__(),
                column_file_step: [None] * datetime_range_idx.__len__(),
                })
            time_tmp = time_tmp.reset_index()
            time_tmp = time_tmp.set_index(time_name_index)

            time_tmp.loc[time_data['time_stamp_restart'], column_file_type] = 'RESTART'
            time_tmp.loc[datetime_obs_idx, column_file_type] = 'OBS'
            if datetime_for_idx is not None:
                time_tmp.loc[datetime_for_idx, column_file_type] = 'FOR'

            time_tmp.loc[time_data['time_stamp_restart'], column_file_pre_processing] = 'PRE_PROCESSING'
            time_tmp.loc[datetime_obs_idx, column_file_pre_processing] = 'PRE_PROCESSING'
            if datetime_for_idx is not None:
                time_tmp.loc[datetime_for_idx, column_file_pre_processing] = 'PRE_PROCESSING'

            time_tmp.loc[time_data['time_stamp_restart'], column_exec_type] = 'NA'
            time_tmp.loc[datetime_obs_idx, column_exec_type] = 'SIM'
            if datetime_for_idx is not None:
                time_tmp.loc[datetime_for_idx, column_exec_type] = 'SIM'
            time_tmp.loc[datetime_tc_idx, column_exec_type] = 'SIM'

            time_tmp.loc[time_data['time_stamp_restart'], column_file_post_processing] = 'NA'
            time_tmp.loc[datetime_obs_idx, column_file_post_processing] = 'POST_PROCESSING'
            if datetime_for_idx is not None:
                time_tmp.loc[datetime_for_idx, column_file_post_processing] = 'POST_PROCESSING'
            time_tmp.loc[datetime_tc_idx, column_file_post_processing] = 'POST_PROCESSING'

            run_list = [time_data['time_run'].strftime(format=time_format_algorithm)]
            run_str = column_sep.join(run_list)
            time_tmp.loc[time_data['time_stamp_restart'], column_exec_eta] = 'NA'
            time_tmp.loc[datetime_obs_idx, column_exec_eta] = run_str
            if datetime_for_idx is not None:
                time_tmp.loc[datetime_for_idx, column_exec_eta] = run_str
            time_tmp.loc[datetime_tc_idx, column_exec_eta] = run_str

            eta_list = [time_data['time_stamp_restart'].strftime(format=time_format_algorithm)]
            eta_str = column_sep.join(eta_list)
            time_tmp.loc[datetime_restart_idx[0], column_file_eta] = eta_str

            for time_step, eta_step in zip(datetime_obs_idx, datetime_obs_eta):
                eta_list = [eta_tmp.strftime(format=time_format_algorithm) for eta_tmp in eta_step]
                eta_str = column_sep.join(eta_list)
                time_tmp.loc[time_step, column_file_eta] = eta_str

            if (datetime_for_idx is not None) and (datetime_for_eta is not None):
                for time_step, eta_step in zip(datetime_for_idx, datetime_for_eta):
                    eta_list = [eta_tmp.strftime(format=time_format_algorithm) for eta_tmp in eta_step]
                    eta_str = column_sep.join(eta_list)
                    time_tmp.loc[time_step, column_file_eta] = eta_str

            if datetime_tc_idx is not None:
                time_tmp.loc[datetime_tc_idx, column_file_type] = 'CORR'

            if datetime_check_idx is not None:
                time_tmp.loc[datetime_check_idx, column_file_check] = True

            time_dict[run_tag] = time_tmp

        return time_dict
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute time info
    def set_time_info(self, run_tag_list=None, time_tc=0, time_ascending=True):

        if run_tag_list is None:
            run_tag_list = 'NA'

        time_run = self.time_run
        time_info_obj = self.obj_time_info_ref

        if ('time_observed_period' in time_info_obj) and ('time_observed_frequency' in time_info_obj):
            time_observed_period = time_info_obj['time_observed_period']
            time_observed_frequency = time_info_obj['time_observed_frequency']
            time_observed_eta = time_info_obj['time_observed_eta']
        else:
            time_observed_period = 0
            time_observed_frequency = 'H'
            time_observed_eta = 'H'
        if 'time_observed_rounding' in time_info_obj:
            time_observed_rounding = time_info_obj['time_observed_rounding']
        else:
            time_observed_rounding = 'H'

        if ('time_forecast_period' in time_info_obj) and ('time_forecast_frequency' in time_info_obj):
            time_forecast_period = time_info_obj['time_forecast_period']
            time_forecast_frequency = time_info_obj['time_forecast_frequency']
            time_forecast_eta = time_info_obj['time_forecast_eta']
        else:
            time_forecast_period = 0
            time_forecast_frequency = 'H'
            time_forecast_eta = 'D'
        if 'time_forecast_rounding' in time_info_obj:
            time_forecast_rounding = time_info_obj['time_forecast_rounding']
        else:
            time_forecast_rounding = 'H'

        if ('time_check_period' in time_info_obj) and ('time_check_frequency' in time_info_obj):
            time_check_period = time_info_obj['time_check_period']
            time_check_frequency = time_info_obj['time_check_frequency']
        else:
            time_check_period = 0
            time_check_frequency = 'H'
        if 'time_check_rounding' in time_info_obj:
            time_check_rounding = time_info_obj['time_check_rounding']
        else:
            time_check_rounding = 'H'

        if ('time_restart_period' in time_info_obj) and ('time_restart_frequency' in time_info_obj):
            time_restart_period = time_info_obj['time_restart_period']
            time_restart_frequency = time_info_obj['time_restart_frequency']
        else:
            time_restart_period = 0
            time_restart_frequency = 'H'
        if 'time_restart_rounding' in time_info_obj:
            time_restart_rounding = time_info_obj['time_restart_rounding']
        else:
            time_restart_rounding = 'D'

        if time_observed_frequency == 'A-OFFSET':
            time_observed_frequency = pd.DateOffset(years=1)

        if not time_observed_frequency[0].isdigit():
            time_observed_frequency = '1' + time_observed_frequency
        time_observed_delta_total_seconds = int(pd.Timedelta(time_observed_frequency).total_seconds())

        if not time_forecast_frequency[0].isdigit():
            time_forecast_frequency = '1' + time_forecast_frequency
        time_forecast_frequency_digit, time_forecast_frequency_char = separate_number_chars(time_forecast_frequency)
        time_forecast_delta_total_seconds = int(pd.Timedelta(time_forecast_frequency).total_seconds())

        if not time_check_frequency[0].isdigit():
            time_check_frequency = '1' + time_check_frequency
        time_check_delta_total_seconds = int(pd.Timedelta(time_check_frequency).total_seconds())

        time_step_obs = time_run
        time_step_obs = time_step_obs.round(freq=time_observed_rounding)
        time_step_for = pd.Timestamp(pd.date_range(start=time_step_obs, periods=2, freq=time_forecast_frequency)[-1])
        time_step_for = time_step_for.round(freq=time_forecast_rounding)

        time_observed_range = pd.date_range(end=time_step_obs, periods=time_observed_period + 1,
                                            freq=time_observed_frequency)

        if time_restart_period > 0:
            time_step_restart = time_observed_range[0]
            time_step_restart = pd.Timestamp(pd.date_range(end=time_step_restart, periods=time_restart_period,
                                                           freq=time_restart_frequency)[0])
            time_step_restart = time_step_restart.floor(freq=time_restart_rounding)

            time_observed_range = pd.date_range(start=time_step_restart, end=time_step_obs,
                                                freq=time_observed_frequency)
            time_restart = pd.date_range(end=time_observed_range[0], freq=time_observed_frequency, periods=2)[0]
        else:
            time_restart = time_observed_range[0]

        time_start = time_observed_range[0]

        if time_forecast_period > 0:
            # eta: Update the time forecast period as a function of run start time (if greater than the nwp start time
            # the time forecast period will be reduced according with the steps between the start nwp time and the run
            # start time
            eta_step_from = time_step_for.floor(time_forecast_eta) + pd.Timedelta(
                int(time_forecast_frequency_digit), unit=time_forecast_frequency_char)
            eta_step_to = time_step_for - pd.Timedelta(
                int(time_forecast_frequency_digit), unit=time_forecast_frequency_char)
            eta_forecast_range = pd.date_range(start=eta_step_from, end=eta_step_to, freq=time_forecast_frequency)

            time_forecast_period = time_forecast_period - eta_forecast_range.shape[0]

            time_forecast_range = pd.date_range(start=time_step_for, periods=time_forecast_period,
                                                freq=time_forecast_frequency)
        else:
            time_forecast_range = None

        if time_observed_period > 0:
            if not time_observed_range.empty:
                time_from = time_observed_range[0]
            else:
                time_from = time_run
        else:
            time_from = time_forecast_range[0]

        if time_forecast_period > 0:
            if not time_forecast_range.empty:
                time_to = time_forecast_range[-1]
            else:
                time_to = time_run
        else:
            time_to = time_observed_range[-1]

        if time_tc > 0:
            time_tc_tmp = pd.date_range(start=time_to, periods=2, freq=time_forecast_frequency)[-1]
            time_tc_range = pd.date_range(start=time_tc_tmp, periods=time_tc, freq=time_forecast_frequency)
            time_to = time_tc_range[-1]
        else:
            time_tc_range = None

        time_run_range = pd.date_range(start=time_from, end=time_to, freq=time_observed_frequency)
        time_run_range = time_run_range.sort_values(return_indexer=False, ascending=time_ascending)

        if time_check_period > 0:
            time_check_range = pd.date_range(end=time_step_obs, periods=time_check_period + 1,
                                             freq=time_check_frequency)
        else:
            time_check_range = None

        time_run_length = time_run_range.__len__()

        time_run_str = convert_timestamp_to_timestring(time_run, time_format_datasets)
        time_start_str = convert_timestamp_to_timestring(time_start, time_format_datasets)
        time_restart_str = convert_timestamp_to_timestring(time_restart, time_format_datasets)

        eta_observed_range = time_observed_range.floor(time_observed_eta).unique()
        eta_observed_list = eta_observed_range.tolist()
        eta_observed_ws = [[eta_step] for eta_step in eta_observed_list]

        if time_forecast_range is not None:
            eta_forecast_range = pd.DatetimeIndex([time_forecast_range.floor(time_forecast_eta).unique()[0]])
            eta_forecast_to = eta_forecast_range
            for i_step in range(1, self.eta_period + 1):
                eta_forecast_from = pd.date_range(end=eta_forecast_to[0], periods=i_step + 1, freq=time_forecast_eta)
                eta_forecast_tmp = pd.DatetimeIndex([eta_forecast_from[0]])
                eta_forecast_range = eta_forecast_range.union(eta_forecast_tmp)
                eta_forecast_range = eta_forecast_range.unique()
            eta_forecast_range = eta_forecast_range.sort_values(ascending=False)
            eta_forecast_list = eta_forecast_range.tolist()
            eta_forecast_ws = [eta_forecast_list] * time_forecast_range.__len__()
        else:
            eta_forecast_ws = None

        time_obj = {}
        for run_tag_step in run_tag_list:
            time_obj[run_tag_step] = {}

            time_obj[run_tag_step]['time_run'] = time_run
            time_obj[run_tag_step]['time_str_run'] = time_run_str
            time_obj[run_tag_step]['time_stamp_start'] = time_start
            time_obj[run_tag_step]['time_str_start'] = time_start_str
            time_obj[run_tag_step]['time_stamp_restart'] = time_restart
            time_obj[run_tag_step]['time_str_restart'] = time_restart_str
            time_obj[run_tag_step]['time_run_range'] = time_run_range
            time_obj[run_tag_step]['time_run_length'] = time_run_length
            time_obj[run_tag_step]['time_check_range'] = time_check_range
            time_obj[run_tag_step]['time_observed_range'] = time_observed_range
            time_obj[run_tag_step]['time_forecast_range'] = time_forecast_range
            time_obj[run_tag_step]['time_observed_eta'] = eta_observed_ws
            time_obj[run_tag_step]['time_forecast_eta'] = eta_forecast_ws
            time_obj[run_tag_step]['time_tc_range'] = time_tc_range
            time_obj[run_tag_step]['time_from'] = time_from
            time_obj[run_tag_step]['time_to'] = time_to
            time_obj[run_tag_step]['time_format'] = time_format_algorithm
            time_obj[run_tag_step]['time_units'] = time_units
            time_obj[run_tag_step]['time_calendar'] = time_calendar
            time_obj[run_tag_step]['time_observed_delta'] = time_observed_delta_total_seconds
            time_obj[run_tag_step]['time_forecast_delta'] = time_forecast_delta_total_seconds
            time_obj[run_tag_step]['time_check_delta'] = time_check_delta_total_seconds
            time_obj[run_tag_step]['time_tc'] = time_tc

        time_df = convert_dict_2_df(time_obj)

        return time_obj, time_df

# -------------------------------------------------------------------------------------
