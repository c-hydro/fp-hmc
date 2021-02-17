"""
Class Features

Name:          drv_dataset_hmc_io_dynamic_summary
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os

import pandas as pd

from copy import deepcopy

from hmc.algorithm.io.lib_data_io_generic import create_darray_2d
from hmc.algorithm.io.lib_data_io_json import write_time_series
from hmc.algorithm.io.lib_data_io_nc import write_collections

from hmc.algorithm.utils.lib_utils_system import create_folder
from hmc.algorithm.utils.lib_utils_string import fill_tags2string
from hmc.algorithm.default.lib_default_args import logger_name, time_format_algorithm

# Log
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to configure datasets
class DSetManager:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, dset,
                 terrain_values=None, terrain_geo_x=None, terrain_geo_y=None, terrain_transform=None,
                 dset_list_format=None,
                 dset_list_type=None,
                 dset_list_group=None,
                 template_time=None,
                 coord_name_geo_x='Longitude', coord_name_geo_y='Latitude', coord_name_time='time',
                 dim_name_geo_x='west_east', dim_name_geo_y='south_north', dim_name_time='time',
                 dset_write_engine='netcdf4', dset_write_compression_level=9, dset_write_format='NETCDF4',
                 file_compression_mode=False, file_compression_ext='.gz',
                 **kwargs):

        if dset_list_format is None:
            dset_list_format = ['Collections', 'TimeSeries']
        if dset_list_type is None:
            dset_list_type = ['ARCHIVE']
        if dset_list_group is None:
            dset_list_group = ['ALL']

        self.dset = dset
        self.dset_list_format = dset_list_format
        self.dset_list_type = dset_list_type
        self.dset_list_group = dset_list_group

        self.terrain_values = terrain_values
        self.terrain_geo_x = terrain_geo_x
        self.terrain_geo_y = terrain_geo_y
        self.terrain_tranform = terrain_transform

        self.da_terrain = create_darray_2d(self.terrain_values, self.terrain_geo_x, self.terrain_geo_y,
                                           coord_name_x=coord_name_geo_x, coord_name_y=coord_name_geo_y,
                                           dim_name_x=dim_name_geo_x, dim_name_y=dim_name_geo_y,
                                           dims_order=[dim_name_geo_y, dim_name_geo_x])

        self.coord_name_time = coord_name_time
        self.coord_name_geo_x = coord_name_geo_x
        self.coord_name_geo_y = coord_name_geo_y
        self.dim_name_time = dim_name_time
        self.dim_name_geo_x = dim_name_geo_x
        self.dim_name_geo_y = dim_name_geo_y

        self.file_name_tag = 'var_file_name'
        self.folder_name_tag = 'var_folder_name'

        dset_obj = {}
        dset_fx = {}
        dset_var_dict = {}
        dset_vars_list = []
        for dset_format in dset_list_format:

            dset_obj[dset_format] = {}
            dset_fx[dset_format] = {}
            dset_var_dict[dset_format] = {}

            if dset_format in self.dset:

                dset_tmp = self.dset[dset_format]

                var_frequency = dset_tmp['hmc_file_frequency']
                var_rounding = dset_tmp['hmc_file_rounding']
                var_operation = dset_tmp['hmc_file_operation']
                var_period = dset_tmp['hmc_file_period']
                var_list = dset_tmp['hmc_file_list']

                dset_fx_list = []
                for var_key, var_value in var_list.items():
                    dset_obj[dset_format][var_key] = {}
                    dset_obj[dset_format][var_key][self.file_name_tag] = var_value['var_file_name']
                    dset_obj[dset_format][var_key][self.folder_name_tag] = var_value['var_file_folder']
                    dset_obj[dset_format][var_key]['var_dset'] = var_value['var_file_dset']
                    dset_obj[dset_format][var_key]['var_format'] = var_value['var_file_format']
                    dset_obj[dset_format][var_key]['var_limits'] = var_value['var_file_limits']
                    dset_obj[dset_format][var_key]['var_units'] = var_value['var_file_units']
                    dset_obj[dset_format][var_key]['var_frequency'] = var_frequency
                    dset_obj[dset_format][var_key]['var_rounding'] = var_rounding
                    dset_obj[dset_format][var_key]['var_operation'] = var_operation
                    dset_obj[dset_format][var_key]['var_period'] = var_period

                    if not dset_var_dict[dset_format]:
                        dset_var_dict[dset_format] = [var_value['var_file_dset']]
                    else:
                        value_list_tmp = dset_var_dict[dset_format]
                        value_list_tmp.append(var_value['var_file_dset'])

                        idx_list_tmp = sorted([value_list_tmp.index(elem) for elem in set(value_list_tmp)])
                        value_list_filter = [value_list_tmp[idx_tmp] for idx_tmp in idx_list_tmp]
                        dset_var_dict[dset_format] = value_list_filter

                    dset_vars_list.append(var_key)
                    dset_fx_list.append(var_operation)

                for var_fx_step in dset_fx_list:
                    for var_fx_key_step, var_fx_flag_step in var_fx_step.items():
                        if var_fx_key_step not in list(dset_fx[dset_format].keys()):
                            dset_fx[dset_format][var_fx_key_step] = var_fx_flag_step
                        else:
                            var_fx_flag_tmp = dset_fx[dset_format][var_fx_key_step]
                            if var_fx_flag_tmp != var_fx_flag_step:
                                log_stream.error(' ===> Variable(s) operation is defined in two different mode!')
                                raise RuntimeError('Different operations are not allowed for the same group')
            else:
                dset_obj[dset_format] = None
                dset_fx[dset_format] = None

        self.dset_obj = dset_obj
        self.dset_fx = dset_fx
        self.dset_vars = list(set(dset_vars_list))
        self.dset_lut = dset_var_dict

        self.template_time = template_time

        self.var_interp = 'nearest'

        self.dset_write_engine = dset_write_engine
        self.dset_write_compression_level = dset_write_compression_level
        self.dset_write_format = dset_write_format
        self.file_compression_mode = file_compression_mode
        self.file_compression_ext = file_compression_ext

        self.file_attributes_dict = {'ncols': self.da_terrain.shape[1], 'nrows': self.da_terrain.shape[0],
                                     'nodata_value': -9999.0,
                                     'xllcorner': self.terrain_tranform[2], 'yllcorner': self.terrain_tranform[5],
                                     'cellsize': self.terrain_tranform[0]}

        self.column_sep = ';'
        self.list_sep = ':'

        self.attrs_selected = ['time_str_run', 'time_str_start', 'time_str_restart', 'time_run_length',
                               'time_format', 'time_units', 'time_calendar',
                               'time_observed_delta', 'time_forecast_delta', 'time_tc'
                               'dam_name_list', 'plant_name_list',
                               'basin_name_list', 'section_name_list', 'outlet_name_list',
                               'run_domain', 'run_name', 'run_mode', 'run_var']

        self.attrs_lut = {'time_str_run': 'time_run', 'time_str_start': 'time_start',
                          'time_str_restart': 'time_restart', 'time_run_length': 'time_length',
                          'time_format': 'time_format', 'time_units': 'time_units', 'time_calendar': 'time_calendar',
                          'time_observed_delta': 'time_observed_delta',
                          'time_forecast_delta': 'time_forecast_delta', 'time_tc': 'time_tc',
                          'dam_name_list': 'dam_name', 'plant_name_list': 'plant_name',
                          'basin_name_list': 'basin_name', 'section_name_list': 'section_name',
                          'outlet_name_list': 'outlet_name',
                          'run_domain': 'run_domain', 'run_name': 'run_name',
                          'run_var': 'run_var', 'run_mode': 'run_mode'}

        self.tag_discharge_section_ts_obs = 'Discharge:section_discharge_obs:{:}'
        self.tag_discharge_section_ts_sim = 'Discharge:section_discharge_sim:{:}'

    # Method to dump data
    def dump_data(self, file_list, file_data, file_time, file_format=None,
                  obj_time=None, obj_static=None, obj_run=None, no_data=-9999.0):

        obj_attrs = {**obj_time, **obj_static, **obj_run}

        file_attrs = {}
        for attr_key, attr_value in obj_attrs.items():
            if attr_key in self.attrs_selected:
                attr_name = self.attrs_lut[attr_key]
                if isinstance(attr_value, list):
                    attr_value_filter = self.list_sep.join(attr_value)
                else:
                    attr_value_filter = attr_value
                file_attrs[attr_name] = attr_value_filter

        # Starting info
        log_stream.info(' --------> Dump data ... ')

        if file_format is not None:
            if file_format == 'netcdf':

                file_path = file_list[0]
                folder_name, file_name = os.path.split(file_path)
                create_folder(folder_name)

                log_stream.info(' ---------> Collections variable(s) file ' + file_name + '... ')
                write_collections(file_path, file_data, file_time, file_attrs=file_attrs)
                log_stream.info(' ---------> Collections variable(s) file ' + file_name + '... DONE')

                log_stream.info(' --------> Dump data ... DONE')

            elif file_format == 'json_time_series':

                outlet_workspace = obj_attrs['Section']
                basin_list = file_attrs['basin_name'].split(self.list_sep)
                section_list = file_attrs['section_name'].split(self.list_sep)
                outlet_list = file_attrs['outlet_name'].split(self.list_sep)

                for file_path, basin_name, section_name, outlet_name in zip(file_list, basin_list,
                                                                            section_list, outlet_list):

                    folder_name, file_name = os.path.split(file_path)
                    create_folder(folder_name)

                    outlet_name = self.list_sep.join([basin_name, section_name])

                    log_stream.info(' --------> Outlet ' + outlet_name +
                                    ' time-series file ' + file_name + '... ')

                    outlet_workspace_default = outlet_workspace[outlet_name]

                    var_name_obs = self.tag_discharge_section_ts_obs.format(outlet_name)
                    var_name_sim = self.tag_discharge_section_ts_sim.format(outlet_name)

                    if var_name_sim in list(file_data.keys()):
                        outlet_data_sim = list(file_data[var_name_sim].values())
                    else:
                        outlet_data_sim = None

                    if var_name_obs in list(file_data.keys()):
                        outlet_data_obs = list(file_data[var_name_obs].values())
                    else:
                        if outlet_data_sim is not None:
                            outlet_data_obs = [no_data] * outlet_data_sim.__len__()
                            log_stream.warning(' ===> Observed datasets is null. Use array with ' +
                                               str(no_data) + ' values')
                        else:
                            outlet_data_obs = None

                    if (outlet_data_obs is not None) and (outlet_data_sim is not None):
                        outlet_time = []
                        for time_stamp in file_time:
                            time_str = time_stamp.strftime(format=time_format_algorithm)
                            outlet_time.append(time_str)

                        outlet_workspace_data = {
                            'time_series_discharge_observed': outlet_data_obs,
                            'time_series_discharge_simulated': outlet_data_sim,
                            'time_period': outlet_time,
                            'time_run': file_attrs['time_run'],
                            'time_start': file_attrs['time_start'],
                            'time_restart': file_attrs['time_restart'],
                            'run_domain': file_attrs['run_domain'],
                            'run_name': file_attrs['run_name'],
                            'run_mode': file_attrs['run_mode'],
                            'run_var': file_attrs['run_var'],
                        }

                        # Define outlet workspace
                        outlet_workspace_obj = {**outlet_workspace_default, **outlet_workspace_data}
                        # Dump data to json file
                        write_time_series(file_path, outlet_workspace_obj)

                        log_stream.info(' --------> Outlet ' + outlet_name +
                                        ' time-series file ' + file_name + '... DONE')

                    else:
                        log_stream.info(' --------> Outlet ' + outlet_name +
                                        ' time-series file ' + file_name + '... FAILED')
                        log_stream.warning(' ===> Observed and simulated datasets are null')

                log_stream.info(' -------> Dump data ... DONE')

            else:
                log_stream.info(' -------> Dump data ... FAILED')
                log_stream.error(' ===> Type of summary format not allowed')
                raise NotImplementedError('Object summary format is not valid')
        else:
            log_stream.info(' -------> Dump data ... SKIPPED. File format is undefined')
            log_stream.warning(' ===> Type of summary format is undefined')

    # Method to define filename of datasets
    def collect_filename(self, time_series, template_run_ref, template_run_filled,
                         tag_exectype='POST_PROCESSING', extra_dict=None):

        dset_obj = self.dset_obj
        lut_obj = self.dset_lut

        time_series_select = time_series.loc[time_series['PostProc_Step'] == tag_exectype]

        datetime_idx_period = time_series_select.index
        exec_type_idx_period = time_series_select['Exec_Type'].values
        exec_eta_idx_period = time_series_select['Exec_ETA'].values

        ws_vars = {}
        dset_vars = {}
        dset_time = {}
        for dset_format, dset_item in dset_obj.items():

            log_stream.info(' ------> Collect ' + dset_format + ' destination filename(s) ... ')

            dset_vars[dset_format] = {}
            dset_time[dset_format] = {}

            dset_lut = lut_obj[dset_format]
            dset_extra = extra_dict[dset_format]

            if dset_format == 'TimeSeries':
                datetime_idx_period_select = [datetime_idx_period[0]]
                exec_type_idx_period_select = [exec_type_idx_period[0]]
                exec_eta_idx_period_select = [exec_eta_idx_period[0]]
            elif dset_format == 'Collections':
                datetime_idx_period_select = [datetime_idx_period[0]]
                exec_type_idx_period_select = [exec_type_idx_period[0]]
                exec_eta_idx_period_select = [exec_eta_idx_period[0]]
            else:
                datetime_idx_period_select = datetime_idx_period
                exec_type_idx_period_select = exec_type_idx_period
                exec_eta_idx_period_select = exec_eta_idx_period

            for (dset_key, dset_value), var_lut in zip(dset_item.items(), dset_lut):

                log_stream.info(' -------> Variable ' + dset_key + ' ... ')

                folder_name_raw = dset_value[self.folder_name_tag]
                file_name_raw = dset_value[self.file_name_tag]

                file_path_list = []
                file_time_list = []
                for datetime_idx_step, exec_type_step, exec_eta_step in zip(
                        datetime_idx_period_select, exec_type_idx_period_select, exec_eta_idx_period_select):

                    datestring_idx_step = pd.Timestamp(datetime_idx_step).to_pydatetime()
                    etastring_idx_step = pd.Timestamp(exec_eta_step).to_pydatetime()

                    template_run_ref_step = deepcopy(template_run_ref)
                    template_run_filled_step = deepcopy(template_run_filled)

                    template_time_filled = dict.fromkeys(list(self.template_time.keys()), datestring_idx_step)
                    # template_time_filled = dict.fromkeys(list(self.template_time.keys()), etastring_idx_step)
                    template_time_filled['dset_datetime_summary'] = etastring_idx_step
                    template_time_filled['dset_sub_path_summary'] = etastring_idx_step
                    template_merge_filled = {**template_run_filled_step, **template_time_filled}

                    template_merge_ref = {**template_run_ref_step, **self.template_time}
                    if dset_format == 'Point':
                        template_merge_ref['dset_var_name_outcome_point'] = var_lut
                        template_merge_ref['dset_var_name_state_point'] = var_lut
                    if dset_format == 'TimeSeries':
                        template_merge_ref['dset_var_name_outcome_ts'] = var_lut
                        template_merge_ref['dset_var_name_state_ts'] = var_lut
                        template_merge_ref['dset_var_name_summary_ts'] = var_lut
                    if dset_format == 'Collections':
                        template_merge_ref['dset_var_name_summary_collections'] = var_lut

                    if dset_extra is None:
                        if (folder_name_raw is not None) and (file_name_raw is not None):
                            folder_name_tmp = fill_tags2string(folder_name_raw, template_merge_ref, template_merge_filled)
                            file_name_tmp = fill_tags2string(file_name_raw, template_merge_ref, template_merge_filled)
                            file_path_list.append(os.path.join(folder_name_tmp, file_name_tmp))
                        else:
                            file_path_list.append(None)
                    else:
                        for basin_name, section_name in zip(dset_extra['basin_name'], dset_extra['section_name']):

                            template_merge_ref['string_var_name_summary_basin'] = basin_name
                            template_merge_ref['string_var_name_summary_section'] = section_name

                            if (folder_name_raw is not None) and (file_name_raw is not None):
                                folder_name_tmp = fill_tags2string(
                                    folder_name_raw, template_merge_ref, template_merge_filled)
                                file_name_tmp = fill_tags2string(
                                    file_name_raw, template_merge_ref, template_merge_filled)
                                file_path_list.append(os.path.join(folder_name_tmp, file_name_tmp))
                            else:
                                file_path_list.append(None)

                    file_time_list.append(datestring_idx_step)

                dset_vars[dset_format][dset_key] = file_path_list
                dset_time[dset_format][dset_key] = file_time_list

                log_stream.info(' -------> Variable ' + dset_key + ' ... DONE')

            dict_vars = dset_vars[dset_format]
            dict_time = dset_time[dset_format]

            df_vars = pd.DataFrame({'Time': datetime_idx_period})
            df_vars['PostProc_Step'] = exec_type_idx_period
            df_vars = df_vars.reset_index()
            df_vars = df_vars.set_index('Time')

            for (var_key, var_time), var_data in zip(dict_time.items(), dict_vars.values()):

                if isinstance(var_data, list):
                    if var_data[0] is not None:
                        var_data_merge = self.list_sep.join(var_data)
                    else:
                        var_data_merge = None
                elif isinstance(var_data, str):
                    var_data_merge = var_data
                else:
                    log_stream.error(' ===> Type of summary data not allowed')
                    raise NotImplementedError('Object summary type is not valid')

                if var_data_merge is not None:
                    time_ts = pd.DatetimeIndex(var_time)
                    var_ts = pd.Series(index=time_ts, data=var_data_merge, name=var_key).fillna(value=pd.NA)
                    df_vars[var_key] = var_ts

            ws_vars[dset_format] = df_vars

        log_stream.info(' ------> Collect ' + dset_format + ' destination filename(s) ... DONE')

        return ws_vars

# -------------------------------------------------------------------------------------
