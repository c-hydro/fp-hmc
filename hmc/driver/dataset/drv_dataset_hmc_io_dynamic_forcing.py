"""
Class Features

Name:          drv_dataset_hmc_io_dynamic_forcing
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import warnings
import os

import numpy as np
import pandas as pd
import xarray as xr

from copy import deepcopy

from hmc.algorithm.io.lib_data_io_generic import swap_darray_dims, create_darray_3d, create_darray_2d, \
    write_dset, create_dset
from hmc.algorithm.io.lib_data_zip_gzip import zip_filename

from hmc.algorithm.utils.lib_utils_system import split_path, create_folder, copy_file
from hmc.algorithm.utils.lib_utils_string import fill_tags2string
from hmc.algorithm.utils.lib_utils_list import flat_list
from hmc.algorithm.utils.lib_utils_zip import add_zip_extension

from hmc.algorithm.default.lib_default_args import logger_name, time_format_algorithm

from hmc.driver.dataset.drv_dataset_hmc_io_type import DSetReader

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
                 terrain_values=None, terrain_geo_x=None, terrain_geo_y=None, terrain_transform=None, terrain_bbox=None,
                 dset_list_format=None,
                 dset_list_type=None,
                 dset_list_group=None,
                 template_time=None,
                 model_tag='hmc', datasets_tag='datasets',
                 coord_name_geo_x='Longitude', coord_name_geo_y='Latitude', coord_name_time='time',
                 dim_name_geo_x='west_east', dim_name_geo_y='south_north', dim_name_time='time',
                 dset_write_engine='netcdf4', dset_write_compression_level=9, dset_write_format='NETCDF4',
                 file_compression_mode=False, file_compression_ext='.gz',
                 **kwargs):

        if dset_list_format is None:
            dset_list_format = ['Gridded', 'Point', 'TimeSeries']
        if dset_list_type is None:
            dset_list_type = ['OBS', 'FOR']
        if dset_list_group is None:
            dset_list_group = ['OBS', 'FOR']

        self.dset = dset
        self.dset_list_format = dset_list_format
        self.dset_list_type = dset_list_type
        self.dset_list_group = dset_list_group

        self.terrain_values = terrain_values
        self.terrain_geo_x = terrain_geo_x
        self.terrain_geo_y = terrain_geo_y
        self.terrain_tranform = terrain_transform
        self.terrain_bbox = terrain_bbox

        self.da_terrain = create_darray_2d(self.terrain_values, self.terrain_geo_x, self.terrain_geo_y,
                                           coord_name_x=coord_name_geo_x, coord_name_y=coord_name_geo_y,
                                           dim_name_x=dim_name_geo_x, dim_name_y=dim_name_geo_y,
                                           dims_order=[dim_name_geo_y, dim_name_geo_x])

        self.model_tag = model_tag
        self.datasets_tag = datasets_tag

        self.coord_name_time = coord_name_time
        self.coord_name_geo_x = coord_name_geo_x
        self.coord_name_geo_y = coord_name_geo_y
        self.dim_name_time = dim_name_time
        self.dim_name_geo_x = dim_name_geo_x
        self.dim_name_geo_y = dim_name_geo_y

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'
        self.var_period_tag = 'var_period'

        dset_obj = {}
        dset_fx = {}
        dset_var_dict = {}
        dset_vars_list = []
        for dset_format in dset_list_format:

            if dset_format in self.dset:

                dset_tmp = self.dset[dset_format]

                dset_obj[dset_format] = {}
                dset_obj[dset_format][model_tag] = {}
                dset_obj[dset_format][datasets_tag] = {}

                dset_fx[dset_format] = {}
                dset_fx[dset_format][datasets_tag] = {}

                dset_var_dict[dset_format] = {}
                dset_var_dict[dset_format][model_tag] = {}

                file_name = dset_tmp['hmc_file_name']
                file_folder = dset_tmp['hmc_file_folder']
                file_format = dset_tmp['hmc_file_format']
                file_frequency = dset_tmp['hmc_file_frequency']
                file_vars = dset_tmp['hmc_file_variable']

                dset_obj[dset_format][model_tag] = {}

                dset_obj[dset_format][model_tag][self.file_name_tag] = file_name
                dset_obj[dset_format][model_tag]['folder_name'] = file_folder
                dset_obj[dset_format][model_tag]['frequency'] = file_format
                dset_obj[dset_format][model_tag]['format'] = file_frequency

                for dset_type in dset_list_type:

                    dset_obj[dset_format][datasets_tag][dset_type] = {}
                    dset_fx[dset_format][datasets_tag][dset_type] = {}
                    if file_vars[dset_type].__len__() > 0:

                        var_frequency = file_vars[dset_type]['var_frequency']
                        var_rounding = file_vars[dset_type]['var_rounding']
                        var_operation = file_vars[dset_type]['var_operation']
                        var_period = file_vars[dset_type]['var_period']
                        var_list = file_vars[dset_type]['var_list']

                        dset_fx_list = []
                        for var_key, var_value in var_list.items():
                            dset_obj[dset_format][datasets_tag][dset_type][var_key] = {}
                            dset_obj[dset_format][datasets_tag][dset_type][var_key][self.file_name_tag] = \
                                var_value['var_file_name']
                            dset_obj[dset_format][datasets_tag][dset_type][var_key][self.folder_name_tag] = \
                                var_value['var_file_folder']
                            dset_obj[dset_format][datasets_tag][dset_type][var_key]['var_dset'] = \
                                var_value['var_file_dset']
                            dset_obj[dset_format][datasets_tag][dset_type][var_key]['var_format'] = \
                                var_value['var_file_format']
                            dset_obj[dset_format][datasets_tag][dset_type][var_key]['var_limits'] = \
                                var_value['var_file_limits']
                            dset_obj[dset_format][datasets_tag][dset_type][var_key]['var_units'] = \
                                var_value['var_file_units']
                            dset_obj[dset_format][datasets_tag][dset_type][var_key]['var_frequency'] = var_frequency
                            dset_obj[dset_format][datasets_tag][dset_type][var_key]['var_rounding'] = var_rounding
                            dset_obj[dset_format][datasets_tag][dset_type][var_key]['var_operation'] = var_operation
                            dset_obj[dset_format][datasets_tag][dset_type][var_key]['var_period'] = var_period

                            if not dset_var_dict[dset_format][model_tag]:
                                dset_var_dict[dset_format][model_tag] = [var_value['var_file_dset']]
                            else:
                                value_list_tmp = dset_var_dict[dset_format][model_tag]
                                value_list_tmp.append(var_value['var_file_dset'])

                                idx_list_tmp = sorted([value_list_tmp.index(elem) for elem in set(value_list_tmp)])
                                value_list_filter = [value_list_tmp[idx_tmp] for idx_tmp in idx_list_tmp]

                                dset_var_dict[dset_format][model_tag] = value_list_filter

                            dset_vars_list.append(var_key)
                            dset_fx_list.append(var_operation)

                        for var_fx_step in dset_fx_list:
                            for var_fx_key_step, var_fx_flag_step in var_fx_step.items():
                                if var_fx_key_step not in list(dset_fx[dset_format][datasets_tag][dset_type].keys()):
                                    dset_fx[dset_format][datasets_tag][dset_type][var_fx_key_step] = var_fx_flag_step
                                else:
                                    var_fx_flag_tmp = dset_fx[dset_format][datasets_tag][dset_type][var_fx_key_step]
                                    if var_fx_flag_tmp != var_fx_flag_step:
                                        log_stream.error(' ===> Variable(s) operation is defined in two different mode!')
                                        raise RuntimeError('Different operations are not allowed for the same group')
                    else:
                        dset_obj[dset_format][datasets_tag][dset_type] = None
                        dset_fx[dset_format][datasets_tag][dset_type] = None

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

        self.terrain_geo_x_llcorner = self.terrain_bbox[0]
        self.terrain_geo_y_llcorner = self.terrain_bbox[1]
        self.terrain_geo_cellsize = self.terrain_tranform[0]

        self.file_attributes_dict = {'ncols': self.da_terrain.shape[1],
                                     'nrows': self.da_terrain.shape[0],
                                     'nodata_value': -9999.0,
                                     'xllcorner': self.terrain_geo_x_llcorner,
                                     'yllcorner': self.terrain_geo_y_llcorner,
                                     'cellsize': self.terrain_geo_cellsize}

        self.column_sep = ';'
        self.list_sep = ':'

    def copy_data(self, dset_model_dyn, dset_source_dyn, columns_excluded=None):

        # Starting info
        log_stream.info(' -------> Copy data ... ')

        if columns_excluded is None:
            columns_excluded = ['index', 'File_Type']

        var_model_list = list(dset_model_dyn.columns)
        var_source_list = list(dset_source_dyn.columns)

        var_model_filter = [var for var in var_model_list if var not in columns_excluded]
        var_source_filter = [var for var in var_source_list if var not in columns_excluded]

        file_dest_list = None
        for var_model_step in var_model_filter:
            file_model_step = list(dset_model_dyn[var_model_step].values)
            for file_name_raw in file_model_step:

                if isinstance(file_name_raw, str):
                    if self.column_sep in file_name_raw:
                        file_name_model_step = file_name_raw.split(self.column_sep)
                    else:
                        file_name_model_step = file_name_raw

                    if not isinstance(file_name_model_step, list):
                        file_name_model_step = [file_name_model_step]

                    if file_dest_list is None:
                        file_dest_list = [[] for i in range(file_name_model_step.__len__())]

                    for list_id, file_dest_step in enumerate(file_name_model_step):
                        if isinstance(file_dest_step, str):
                            file_dest_list[list_id].append(file_dest_step)
                        else:
                            log_stream.warning(' ===> Expected filename is not in string format!')

        file_source_list = None
        list_id_defined = None
        for list_id, var_source_step in enumerate(var_source_filter):

            log_stream.info(' --------> Variable ' + var_source_step + ' ... ')
            file_source_step = list(dset_source_dyn[var_source_step].values)

            file_source_tmp = []
            for file_name_raw in file_source_step:

                if isinstance(file_name_raw, str):
                    if self.column_sep in file_name_raw:
                        file_name_source_step = file_name_raw.split(self.column_sep)
                    else:
                        file_name_source_step = file_name_raw

                    if not isinstance(file_name_source_step, list):
                        file_name_source_step = [file_name_source_step]

                    for file_source_step in file_name_source_step:
                        if isinstance(file_source_step, str):
                            file_source_tmp.append(file_source_step)
                        else:
                            log_stream.warning(' ===> Expected filename is not in string format!')

            if file_source_list is None:
                file_source_list = []

            if not file_source_tmp:
                file_source_list = None
            else:
                file_source_list.append(file_source_tmp)

                if list_id_defined is None:
                    list_id_defined = 0
                else:
                    list_id_defined += 1

            if (file_dest_list is not None) and (file_source_list is not None):

                if file_dest_list.__len__() > file_source_list.__len__():
                    file_dest_select = flat_list(file_dest_list)
                    file_source_select = file_source_list[list_id_defined]
                elif file_dest_list.__len__() == file_source_list.__len__():
                    file_dest_select = file_dest_list[list_id]
                    file_source_select = file_source_list[list_id]
                else:
                    log_stream.error(' ===> Copy failed for unexpected number of destination or source filenames')
                    raise IOError('Source and destination filenames have to be equal')

                if file_dest_select and file_source_select:

                    for file_path_dest_step, file_path_source_step in zip(file_dest_select, file_source_select):

                        folder_name_source_step, file_name_source_step = split_path(file_path_source_step)
                        folder_name_dest_step, file_name_dest_step = split_path(file_path_dest_step)

                        if os.path.exists(file_path_source_step):
                            create_folder(folder_name_dest_step)
                            copy_file(file_path_source_step, file_path_dest_step)
                        else:
                            log_stream.warning(' ===> Copy file: ' + file_name_source_step +
                                               ' FAILED. File does not exist!')
            else:
                log_stream.warning(' ===> Copy file: ... FAILED. All files do not exist')

            log_stream.info(' --------> Variable ' + var_source_step + ' ... DONE')

        # Ending info
        log_stream.info(' -------> Copy data ... DONE')

    def freeze_data(self, dset_expected, dset_def, dset_key_delimiter=':', dset_key_excluded=None):

        # Starting info
        log_stream.info(' -------> Freeze data ... ')

        if dset_key_excluded is None:
            dset_key_excluded = ['index', 'File_Type', 'terrain']

        if dset_def is not None:

            dset_vars_expected = self.dset_vars

            dset_check = False
            dframe_check = False
            if isinstance(dset_def, xr.Dataset):
                dset_vars_def = list(dset_def.data_vars)
                dset_check = True
            elif isinstance(dset_def, pd.DataFrame):
                dset_vars_def = list(dset_def.columns)
                dframe_check = True
            else:
                log_stream.error(' ===> Freeze data type is not implemented')
                raise NotImplementedError('Data type is unknown for freezing data')

            dset_vars_tmp = deepcopy(dset_vars_def)
            for dset_var_step in dset_vars_tmp:
                if dset_var_step in dset_key_excluded:
                    dset_vars_def.remove(dset_var_step)

            for dset_var_step in dset_vars_def:

                if dset_key_delimiter in dset_var_step:
                    dset_var_root = dset_var_step.split(dset_key_delimiter)[0]
                else:
                    dset_var_root = dset_var_step

                if dset_vars_expected[0] == 'ALL':

                    if dset_check:

                        if dset_var_step != 'terrain':

                            values_nan = np.zeros([dset_expected.index.__len__()])
                            values_nan[:] = np.nan
                            dset_expected[dset_var_step] = values_nan

                            time_array = dset_def[dset_var_step].time.values
                            time_stamp_list = []
                            for time_step in time_array:
                                time_stamp = pd.to_datetime(time_step, format='%Y-%m-%d_%H:%M:%S')
                                time_stamp_list.append(time_stamp)
                            dset_idx = pd.DatetimeIndex(time_stamp_list)
                            dset_values = dset_def[dset_var_step].values

                            dset_expected.loc[dset_idx, dset_var_step] = dset_values

                    elif dframe_check:

                        dset_idx = dset_def[dset_var_step].index
                        dset_values = dset_def[dset_var_step].values

                        dset_expected.loc[dset_idx, dset_var_step] = dset_values

                    else:
                        log_stream.error(' ===> Freeze data type for ALL variables is not implemented')
                        raise NotImplementedError('Data type is unknown for freezing data')

                elif dset_var_root in dset_vars_expected:
                    if dset_var_step not in list(dset_expected.columns):
                        values_nan = np.zeros([dset_expected.index.__len__()])
                        values_nan[:] = np.nan
                        dset_expected[dset_var_step] = values_nan

                    if dset_check:

                        time_array = dset_def[dset_var_step].time.values
                        time_stamp_list = []
                        for time_step in time_array:
                            time_stamp = pd.to_datetime(time_step, format='%Y-%m-%d_%H:%M:%S')
                            time_stamp_list.append(time_stamp)
                        dset_idx = pd.DatetimeIndex(time_stamp_list)
                        dset_values = dset_def[dset_var_step].values

                    elif dframe_check:

                        dset_idx = dset_def[dset_var_step].index
                        dset_values = dset_def[dset_var_step].values

                    else:
                        log_stream.error(' ===> Freeze data type for variable is not implemented')
                        raise NotImplementedError('Data type is unknown for freezing data')

                    dset_expected.loc[dset_idx, dset_var_step] = dset_values
                else:
                    pass

        # Ending info
        log_stream.info(' -------> Freeze data ... DONE')

        return dset_expected

    def dump_data(self, dset_model, dset_time, dset_source):

        # Starting info
        log_stream.info(' -------> Dump data ... ')

        dump_status_list = []
        file_path_list_unzip = []
        file_path_list_zip = []
        for time_step in dset_time:

            if time_step in list(dset_source[self.dim_name_time].values):

                dset_step = dset_source.sel(time=time_step)
                dset_file_path_step = dset_model.loc[time_step][self.model_tag]

                dset_file_folder_step, dset_file_name_step = split_path(dset_file_path_step)
                create_folder(dset_file_folder_step)

                if self.file_compression_mode:
                    if not dset_file_name_step.endswith(self.file_compression_ext):
                        log_stream.warning(
                            ' ===> File expected in zipped format with ' + self.file_compression_ext + ' extension. Got '
                            + dset_file_name_step + ' filename. Add extension to given filename')
                        dset_file_name_step = add_zip_extension(dset_file_name_step, self.file_compression_ext)

                if dset_file_name_step.endswith(self.file_compression_ext):
                    dset_file_name_step_zip = dset_file_name_step
                    dset_file_name_step_unzip = os.path.splitext(dset_file_name_step)[0]
                else:
                    dset_file_name_step_zip = dset_file_name_step
                    dset_file_name_step_unzip = dset_file_name_step
                    self.file_compression_mode = True

                dset_file_path_step_zip = os.path.join(dset_file_folder_step, dset_file_name_step_zip)
                dset_file_path_step_unzip = os.path.join(dset_file_folder_step, dset_file_name_step_unzip)

                # Write dset
                log_stream.info(' --------> Filename ' + dset_file_name_step_unzip + ' ... ')

                dset_attrs = self.file_attributes_dict
                write_dset(dset_file_path_step_unzip,
                           dset_data=dset_step, dset_attrs=dset_attrs, dset_format=self.dset_write_format,
                           dset_compression=self.dset_write_compression_level, dset_engine=self.dset_write_engine)
                log_stream.info(' --------> Filename ' + dset_file_name_step_unzip + ' ... DONE')

                file_path_list_unzip.append(dset_file_path_step_unzip)
                file_path_list_zip.append(dset_file_path_step_zip)

                dump_status_list.append(True)

            else:
                log_stream.warning(' ===> Dump time step ' + str(time_step) + ' skipped. Time step is not in datasets')

        # Ending info
        log_stream.info(' -------> Dump data ... DONE')

        # Starting info
        log_stream.info(' -------> Zip data ... ')

        file_compression_mode = self.file_compression_mode
        if file_compression_mode:
            for file_path_unzip, file_path_zip, dump_status in zip(file_path_list_unzip, file_path_list_zip,
                                                                   dump_status_list):

                if dump_status:

                    if os.path.exists(file_path_zip):
                        os.remove(file_path_zip)

                    if os.path.exists(file_path_unzip):
                        zip_filename(file_path_unzip, file_path_zip)
                    else:
                        # Ending info
                        log_stream.warning(' -------> Zip data ... SKIPPED. File ' + file_path_unzip + ' not available')

                    if os.path.exists(file_path_zip) and os.path.exists(file_path_unzip):
                        os.remove(file_path_unzip)

                else:
                    # Ending info
                    log_stream.warning(' -------> Zip data ... SKIPPED. File' + file_path_unzip + ' not saved')

            # Ending info
            log_stream.info(' -------> Zip data ... DONE')

        else:
            # Ending info
            log_stream.info(' -------> Zip data ... SKIPPED. Zip not activated')

    def organize_data(self, dset_time, dset_source, dset_variable_selected='ALL'):

        # Get variable(s)
        dset_vars = dset_source[self.datasets_tag]
        # Get terrain reference
        da_terrain = self.da_terrain

        if dset_vars is not None:
            if (self.coord_name_geo_x in list(dset_source.keys())) and (self.coord_name_geo_x in list(dset_source.keys())):

                if dset_variable_selected == 'ALL':
                    dset_variable_selected = dset_vars.variables

                log_stream.info(' -------> Organize gridded datasets ... ')

                if dset_variable_selected is not None:

                    # Get geographical information
                    geo_x_values = dset_source[self.coord_name_geo_x]
                    geo_y_values = dset_source[self.coord_name_geo_y]

                    # Iterate over dataset(s)
                    var_dset_collections = None
                    var_dset_out = None
                    for var_name_step in dset_vars:

                        log_stream.info(' --------> Organize ' + var_name_step + ' datasets ... ')

                        if var_name_step in dset_variable_selected:

                            # Get data array
                            var_da_step = dset_vars[var_name_step]

                            if var_da_step is not None:

                                # Get dataset coordinates list
                                dims_list = list(var_da_step.dims)

                                if 'time' in dims_list:
                                    time_stamp_period = []
                                    for time_step in var_da_step['time'].values:
                                        timestamp_step = pd.to_datetime(time_step, format='%Y-%m-%d_%H:%M:%S')
                                        timestamp_step = timestamp_step.round('H')
                                        time_stamp_period.append(timestamp_step)
                                    dset_time_step = pd.DatetimeIndex(time_stamp_period)

                                    if isinstance(dset_time, pd.Timestamp):
                                        dset_time = pd.DatetimeIndex([dset_time])

                                    # Recompute period in case of time_start and/or time end are not the same
                                    dset_time_step_start = dset_time_step.values[0]
                                    dset_time_step_end = dset_time_step.values[-1]

                                    dset_time_start = dset_time.values[0]
                                    dset_time_end = dset_time.values[-1]

                                    if dset_time_step_start < dset_time_start:
                                        index_start_step_tmp = dset_time_step.get_loc(dset_time_start)
                                        index_start_tmp = dset_time.get_loc(dset_time_start)
                                    elif dset_time_step_start == dset_time_start:
                                        index_start_step_tmp = 0
                                        index_start_tmp = 0
                                    else:
                                        log_stream.error(' ===> Time start is greater than time start step.')
                                        log_stream.error(' ===> Errors occurred for unreal condition')
                                        raise NotImplementedError('Case not implemented yet')

                                    if dset_time_step_end < dset_time_end:
                                        index_end_step_tmp = dset_time_step.get_loc(dset_time_step_end) + 1
                                        index_end_tmp = dset_time.get_loc(dset_time_step_end) + 1
                                    elif dset_time_step_end == dset_time_end:
                                        index_end_step_tmp = dset_time_step.get_loc(dset_time_end) + 1
                                        index_end_tmp = dset_time.get_loc(dset_time_end) + 1
                                    elif dset_time_step_end > dset_time_end:
                                        index_end_step_tmp = dset_time_step.get_loc(dset_time_end) + 1
                                        index_end_tmp = dset_time.get_loc(dset_time_end) + 1
                                    else:
                                        log_stream.error(' ===> Matching between time start and time start step failed')
                                        log_stream.error(' ===> Errors occurred for unknown reason')
                                        raise NotImplementedError('Case not implemented yet')

                                    dset_time_step = dset_time_step[index_start_step_tmp:index_end_step_tmp]
                                    var_da_step = var_da_step[:, :, index_start_step_tmp:index_end_step_tmp]

                                    dset_time = dset_time[index_start_tmp:index_end_tmp]

                                    # Search index of longitude and latitude
                                    if self.dim_name_geo_x in dims_list:
                                        dim_idx_geo_x = dims_list.index(self.dim_name_geo_x)
                                    else:
                                        log_stream.error(' ===> Dimension X is wrong defined.')
                                        raise IOError('Check netcdf datasets for dims definition')

                                    if self.dim_name_geo_y in dims_list:
                                        dim_idx_geo_y = dims_list.index(self.dim_name_geo_y)
                                    else:
                                        log_stream.error(' ===> Dimension Y is wrong defined.')
                                        raise IOError('Check netcdf datasets for dims definition')

                                    # Get variable, data, time and attributes of expected data
                                    var_data_expected = np.zeros(
                                        [var_da_step.shape[dim_idx_geo_y], var_da_step.shape[dim_idx_geo_x],
                                         dset_time.shape[0]])
                                    # Check datasets dimensions and in case of mismatching try to correct
                                    if var_data_expected.shape[:2] != da_terrain.shape:
                                        var_data_expected = np.zeros([da_terrain.shape[0], da_terrain.shape[1],
                                                                     dset_time.shape[0]])
                                        log_stream.info(' --------> ' + var_name_step +
                                                        ' datasets and terrain datasets have not the same dimensions'
                                                        ' found by using the automatic detection')
                                        log_stream.warning(' ===> Use terrain dimensions to try datasets analysis')
                                    else:
                                        log_stream.info(' --------> ' + var_name_step +
                                                        ' datasets and terrain datasets have the same dimensions'
                                                        ' found by using the automatic detection')

                                    var_data_expected[:, :, :] = np.nan

                                    # Get variable, data, time and attributes of expected data
                                    var_da_expected = create_darray_3d(
                                        var_data_expected, dset_time, geo_x_values, geo_y_values,
                                        coord_name_time=self.coord_name_time,
                                        coord_name_x=self.coord_name_geo_x, coord_name_y=self.coord_name_geo_y,
                                        dim_name_time=self.dim_name_time,
                                        dim_name_x=self.dim_name_geo_x, dim_name_y=self.dim_name_geo_y,
                                        dims_order=[self.dim_name_geo_y, self.dim_name_geo_x, self.dim_name_time])

                                    # Swap data arrays dimensions (is needed for mismatching in data input)
                                    var_da_step = swap_darray_dims(var_da_expected, var_da_step, da_terrain)
                                    # Combine raw and expected data arrays
                                    var_da_combined = var_da_expected.combine_first(var_da_step)

                                    # Select only selected time-steps
                                    dset_time_intersect = dset_time_step.intersection(dset_time)
                                    if dset_time_intersect.shape == dset_time.shape:
                                        var_da_selected = var_da_combined.sel(time=dset_time)
                                    else:
                                        log_stream.error(
                                            ' ===> All/some selected time-steps are not available in source data.')
                                        raise IOError('Datasets are not on the same period or sub-period.')

                                    # Perform interpolation and masking of datasets
                                    if self.var_interp == 'nearest':
                                        var_da_interp = var_da_selected.interp(
                                            south_north=self.da_terrain['south_north'],
                                            west_east=self.da_terrain['west_east'], method='nearest')
                                    else:
                                        # Ending info for undefined function
                                        log_stream.error(' ===> Interpolation method not available')
                                        raise NotImplemented('Interpolation method not implemented yet')

                                    var_da_masked = var_da_interp.where(self.da_terrain != -9999)

                                else:

                                    if isinstance(dset_time, pd.Timestamp):
                                        dset_time = pd.DatetimeIndex([dset_time])

                                    var_da_masked = var_da_step.where(self.da_terrain != -9999)

                                    if var_da_masked.ndim == 3:
                                        list_dims = list(var_da_masked.dims)
                                        if self.dim_name_geo_x in list_dims:
                                            list_dims.remove(self.dim_name_geo_x)
                                        if self.dim_name_geo_y in list_dims:
                                            list_dims.remove(self.dim_name_geo_y)
                                        dim_name = list_dims[0]

                                        with warnings.catch_warnings():
                                            warnings.simplefilter("ignore")
                                            var_da_masked = var_da_masked.mean(dim=dim_name)

                                        var_da_masked = var_da_masked.expand_dims('time', axis=-1)
                                        var_da_masked.assign_coords({'time': dset_time})

                                    elif var_da_masked.ndim > 3:
                                        log_stream.error(' ===> Variable dimensions not allowed')
                                        raise IOError('Case not implemented yet')

                                log_stream.info(' --------> Organize ' + var_name_step + ' datasets ... DONE')

                            else:

                                log_stream.info(' --------> Organize ' + var_name_step + ' datasets ... FAILED')
                                log_stream.warning(' ===> Variable is None. Default initialization was selecting')

                                var_data_null = np.zeros([var_da_step.shape[0], var_da_step.shape[1], dset_time.shape[0]])
                                var_data_null[:, :, :] = np.nan
                                var_da_masked = create_darray_3d(
                                    var_data_null, dset_time, geo_x_values, geo_y_values,
                                    coord_name_time=self.coord_name_time,
                                    coord_name_x=self.coord_name_geo_x, coord_name_y=self.coord_name_geo_y,
                                    dim_name_time=self.dim_name_time,
                                    dim_name_x=self.dim_name_geo_x, dim_name_y=self.dim_name_geo_y,
                                    dims_order=[self.dim_name_geo_y, self.dim_name_geo_x, self.dim_name_time])

                            # Organize data in a common datasets
                            var_dset_grid_step = create_dset(var_data_time=dset_time,
                                                             var_data_name=var_name_step, var_data_values=var_da_masked,
                                                             var_data_attrs=None,
                                                             var_geo_1d=False,
                                                             file_attributes=self.file_attributes_dict,
                                                             var_geo_name='terrain', var_geo_values=self.terrain_values,
                                                             var_geo_x=self.terrain_geo_x, var_geo_y=self.terrain_geo_y,
                                                             var_geo_attrs=None)

                            # Compute average values
                            var_dset_ts_step = var_dset_grid_step.mean(dim=['south_north', 'west_east'])

                            if var_dset_out is None:
                                var_dset_out = var_dset_grid_step
                            else:
                                var_dset_out = var_dset_out.merge(var_dset_grid_step, join='right')

                            if var_dset_collections is None:
                                var_dset_collections = var_dset_ts_step
                            else:
                                var_dset_collections = var_dset_collections.merge(var_dset_ts_step, join='right')

                        else:
                            log_stream.info(' --------> Organize ' + var_name_step +
                                            ' datasets ... SKIPPED. Variable is not selected for analysis.')

                    log_stream.info(' -------> Organize gridded datasets ... DONE')

                else:
                    var_dset_out = None
                    var_dset_collections = None
                    log_stream.info(' -------> Organize gridded datasets ... SKIPPED. Empty selected variables.')

            else:

                log_stream.info(' -------> Organize point and time-series datasets ... ')

                if dset_variable_selected is not None:

                    if dset_variable_selected == 'ALL':
                        dset_variable_selected = list(dset_vars.keys())

                    if isinstance(dset_time, pd.Timestamp):
                        dset_time = pd.DatetimeIndex([dset_time])

                    var_dset_collections = pd.DataFrame({self.dim_name_time: dset_time})
                    for dset_key, dset_group in dset_vars.items():

                        log_stream.info(' --------> Organize ' + dset_key + ' datasets ... ')

                        if dset_key in dset_variable_selected:
                            for dset_sub_key, dset_sub_group in dset_group.items():
                                for dset_sub_col in list(dset_sub_group.columns):
                                    var_key = ':'.join([dset_key, dset_sub_key, dset_sub_col])
                                    var_data = dset_sub_group[dset_sub_col].values
                                    var_dset_collections.loc[:, var_key] = pd.Series(data=var_data).fillna(value=pd.NA)
                            log_stream.info(' --------> Organize ' + dset_key + ' datasets ... DONE')
                        else:
                            log_stream.info(' --------> Organize ' + var_name_step +
                                            ' datasets ... SKIPPED. Variable is not selected for analysis.')

                    var_dset_collections = var_dset_collections.reset_index()
                    var_dset_collections = var_dset_collections.set_index(self.dim_name_time)

                    var_dset_out = None

                    log_stream.info(' -------> Organize point and time-series datasets ... DONE')

                else:
                    var_dset_out = None
                    var_dset_collections = None
                    log_stream.info(
                        ' -----> Organize point and time-series datasets ... SKIPPED. Empty selected variables.')

        else:

            log_stream.warning(' ===> Datasets is None. All variable(s) are undefined')

            var_dset_out = None
            var_dset_collections = None

        return var_dset_out, var_dset_collections

    def collect_data(self, dset_model_dyn, dset_source_dyn, dset_source_base,
                     dset_static_info=None,
                     columns_excluded=None, dset_time_info=None,
                     dset_time_start=None, dset_time_end=None, **kwargs):

        if columns_excluded is None:
            columns_excluded = ['index', 'File_Type']

        var_args = {}
        if 'plant_name_list' in kwargs:
            var_args['plant_name_list'] = kwargs['plant_name_list']

        file_source_vars_tmp = list(dset_source_dyn.columns)
        file_source_vars_def = [elem for elem in file_source_vars_tmp if elem not in columns_excluded]

        var_frame = {}
        dset_source = None
        for var_name in file_source_vars_def:

            log_stream.info(' -------> Collect ' + var_name + ' source datasets ... ')

            if dset_source_base is not None:

                if var_name in list(dset_source_base.keys()):

                    dset_source_var_base = dset_source_base[var_name]
                    dset_source_var_dyn = dset_source_dyn[var_name]

                    dset_datetime_idx = dset_source_var_dyn.index
                    dset_filename = dset_source_var_dyn.values

                    if 'format' in dset_source_base:
                        dset_format = dset_source_base['format']
                    else:
                        dset_format = None

                    if dset_static_info is not None:
                        if var_name == 'Discharge':
                            var_static_info = dset_static_info['outlet_name_list']
                        elif (var_name == 'DamV') or (var_name == 'DamL'):
                            var_static_info = dset_static_info['dam_name_list']
                        elif var_name == 'VarAnalysis':
                            var_static_info = None
                        else:
                            var_static_info = None
                    else:
                        var_static_info = None

                    driver_hmc_parser = DSetReader(dset_filename, dset_source_var_base, dset_datetime_idx,
                                                   dset_time_info, var_format=dset_format)

                    obj_var, da_time, geo_x, geo_y = driver_hmc_parser.read_filename_dynamic(
                        var_name, var_args, var_time_start=dset_time_start, var_time_end=dset_time_end,
                        var_static_info=var_static_info)

                    if obj_var is not None:
                        if isinstance(obj_var, xr.Dataset):
                            if self.coord_name_geo_x not in list(var_frame.keys()):
                                var_frame[self.coord_name_geo_x] = geo_x
                            if self.coord_name_geo_y not in list(var_frame.keys()):
                                var_frame[self.coord_name_geo_y] = geo_y

                            obj_var_name_list = list(obj_var.data_vars)
                            if obj_var_name_list.__len__() == 1:

                                log_stream.info(' --------> Variable list: ' + str(obj_var_name_list) +
                                                ' with 1 item')

                                obj_var_name = obj_var_name_list[0]

                                if obj_var_name != var_name:
                                    obj_var = obj_var.rename_vars({obj_var_name: var_name})
                                    log_stream.warning(' ===> Switch variable name in dataset from "' +
                                                       obj_var_name + '" to "' + var_name + '"')

                            else:
                                log_stream.info(' --------> Variable list: ' + str(obj_var_name_list) +
                                                ' with ' + str(obj_var_name_list.__len__()) + ' items')

                            if dset_source is None:
                                dset_source = obj_var
                            else:
                                dset_source = dset_source.combine_first(obj_var)
                        elif isinstance(obj_var, dict):
                            if dset_source is None:
                                dset_source = {}

                            if var_name == 'ALL':
                                if isinstance(obj_var, dict):
                                    obj_tmp = list(obj_var.values())[0]
                                    var_name = obj_tmp.name

                            dset_source[var_name] = obj_var
                        else:
                            log_stream.error(' ===> Data dynamic object is not allowed')
                            raise NotImplementedError('Object dynamic type is not valid')

                    log_stream.info(' -------> Collect ' + var_name + ' source datasets ... DONE')
                else:
                    log_stream.warning(' ===> Variable is not available in the datasets')
                    log_stream.info(' -------> Collect ' + var_name + ' source datasets ... FAILED')
            else:
                log_stream.warning(' ===> Type datasets is not defined')
                log_stream.info(' -------> Collect ' + var_name + ' source datasets ... FAILED')

        var_frame[self.datasets_tag] = dset_source

        return var_frame

    # Method to define filename of datasets
    def collect_filename(self, time_series, template_run_ref, template_run_filled,
                         extra_dict=None):

        dset_obj = self.dset_obj
        dset_lut = self.dset_lut

        datetime_idx_period = time_series.index
        filetype_idx_period = time_series['File_Type'].values
        filegroup_values_period = time_series['File_Group'].values
        fileeta_values_period = time_series['File_ETA'].values

        filegroup_values_period = filegroup_values_period[~np.isnan(filegroup_values_period)]
        filegroup_idx_period = filegroup_values_period.tolist()
        filegroup_idx_unique = set(filegroup_idx_period)
        filegroup_idx_start = [filegroup_idx_period.index(x) for x in filegroup_idx_unique]

        if extra_dict is not None:
            template_run_extra = extra_dict
            template_keys_extra = list(template_run_extra.keys())
        else:
            template_run_extra = None
            template_keys_extra = None

        ws_vars = {}
        dset_vars = {}
        dset_time = {}
        for dset_format, dset_workspace in dset_obj.items():

            log_stream.info(' ------> Collect ' + dset_format + ' source filename(s) ... ')

            dset_vars[dset_format] = {}
            dset_time[dset_format] = {}

            dset_item = dset_workspace[self.datasets_tag]

            for dset_step_type, dset_step_group in zip(self.dset_list_type, self.dset_list_group):

                log_stream.info(' -------> Type ' + dset_step_type + ' ... ')

                if dset_format == 'TimeSeries':

                    filegroup_idx_select = [idx for type, idx in zip(
                        filetype_idx_period[filegroup_idx_start], filegroup_idx_start) if type in self.dset_list_type]
                    filetype_idx_select = filetype_idx_period[filegroup_idx_select]

                    filegroup_idx_step = None
                    filetype_idx_period_tmp = []
                    datetime_idx_period_tmp = []
                    for filegroup_idx_step in filegroup_idx_select:
                        datetime_idx_period_tmp.append(datetime_idx_period[filegroup_idx_step])
                        filetype_idx_period_tmp.append(filetype_idx_period[filegroup_idx_step])
                        break
                    datetime_idx_period_tmp = pd.DatetimeIndex(datetime_idx_period_tmp)
                    datetime_idx_select = pd.DatetimeIndex([time_series.index[filegroup_idx_step]])
                    eta_array_select = np.array([fileeta_values_period[filegroup_idx_step]])

                else:

                    group_condition = time_series['File_Type'].str.contains(dset_step_group)

                    time_df_select = time_series[group_condition]
                    datetime_idx_select = time_df_select.index
                    eta_array_select = fileeta_values_period[group_condition]

                    datetime_idx_period_tmp = datetime_idx_period
                    filetype_idx_period_tmp = filetype_idx_period

                dset_type = dset_item[dset_step_type]
                if dset_type is not None:

                    for dset_key, dset_value in dset_type.items():

                        log_stream.info(' --------> Variable ' + dset_key + ' ... ')
                        dset_null_check = False

                        folder_name_raw = dset_value[self.folder_name_tag]
                        file_name_raw = dset_value[self.file_name_tag]

                        file_period = dset_value[self.var_period_tag]

                        file_path_list = []
                        file_time_list = []
                        file_time_ts = []
                        message_condition = True

                        if (dset_step_type == 'FOR') and (file_period == 1):

                            log_stream.info(' ---------> Update datasets ETA of ' + dset_step_type
                                            + ' with a period equal to ' + str(file_period) + ' ... ')

                            eta_list_recomputed = []
                            for datetime_idx_step in datetime_idx_select:
                                eta_list_recomputed.append(datetime_idx_step.strftime(time_format_algorithm))
                            eta_array_recomputed = np.array(eta_list_recomputed)
                            eta_array_select = deepcopy(eta_array_recomputed)

                            log_stream.info(' ---------> Update datasets ETA of ' + dset_step_type
                                            + ' with a period equal to ' + str(file_period) + ' ... DONE')

                        for datetime_idx_step, eta_array_step in zip(datetime_idx_select, eta_array_select):

                            if dset_null_check:
                                break

                            datetime_step = datetime_idx_step.to_pydatetime()
                            eta_list_step = eta_array_step.split(';')

                            folder_name_sel = None
                            file_name_sel = None
                            file_time_sel = None
                            file_time_memory = None
                            for eta_list_tmp in eta_list_step:

                                datetime_eta_step = pd.Timestamp(eta_list_tmp).to_pydatetime()

                                template_run_ref_step = deepcopy(template_run_ref)
                                template_run_filled_step = deepcopy(template_run_filled)

                                if dset_format == 'TimeSeries':
                                    if template_run_extra is not None:
                                        template_merge_ref = {**template_run_ref_step, **template_run_extra}
                                        template_run_filled_step = {**template_run_filled_step, **template_merge_ref}

                                template_time_filled = dict.fromkeys(list(self.template_time.keys()), datetime_eta_step)
                                template_merge_filled = {**template_run_filled_step, **template_time_filled}

                                template_merge_ref = {**template_run_ref_step, **self.template_time}

                                folder_name_tmp = fill_tags2string(folder_name_raw, template_merge_ref, template_merge_filled)
                                file_name_tmp = fill_tags2string(file_name_raw, template_merge_ref, template_merge_filled)

                                if isinstance(folder_name_tmp, list) and isinstance(file_name_tmp, list):
                                    for folder_name_tmp_step, file_name_tmp_step in zip(folder_name_tmp, file_name_tmp):
                                        if os.path.exists(os.path.join(folder_name_tmp_step, file_name_tmp_step)):
                                            if folder_name_sel is None:
                                                folder_name_sel = folder_name_tmp
                                            if file_name_sel is None:
                                                file_name_sel = file_name_tmp
                                            if file_time_sel is None:
                                                file_time_sel = datetime_step
                                                file_time_memory = datetime_eta_step
                                elif isinstance(folder_name_tmp, str) and isinstance(file_name_tmp, str):
                                    folder_name_sel = folder_name_tmp
                                    file_name_sel = file_name_tmp
                                    file_time_sel = datetime_step

                                    if eta_list_step.__len__() > 1:
                                        if os.path.exists(os.path.join(folder_name_sel, file_name_sel)):
                                            break
                                        else:
                                            folder_name_sel = None
                                            file_name_sel = None
                                            file_time_sel = None

                                elif (folder_name_tmp is None) or (file_name_tmp is None):
                                    log_stream.info(' --------> Variable ' + dset_key +
                                                    ' ... SKIPPED. Datasets folder or filename are null.')
                                    dset_null_check = True
                                    break
                                else:
                                    log_stream.info(' ------> Collect ' + dset_format + ' source filename(s) ... FAILED')
                                    log_stream.error(' ===> Collect dynamic datasets filename(s) failed!')
                                    raise NotImplementedError('Type of folder or file name is not supported')

                            if isinstance(folder_name_sel, list) and isinstance(file_name_sel, list):
                                for folder_name_sel_step, file_name_sel_step in zip(folder_name_sel, file_name_sel):
                                    file_path_sel = os.path.join(folder_name_sel_step, file_name_sel_step)
                                    if file_path_sel not in file_path_list:
                                        file_path_list.append(file_path_sel)
                                if file_time_memory not in file_time_ts:
                                    file_time_list.append(file_time_sel)
                                    file_time_ts.append(file_time_memory)
                            elif isinstance(folder_name_sel, str) and isinstance(file_name_sel, str):
                                if (folder_name_sel is not None) and (file_name_sel is not None):
                                    file_path_list.append(os.path.join(folder_name_sel, file_name_sel))
                                    file_time_list.append(file_time_sel)
                            elif (folder_name_sel is None) and (file_name_sel is None):
                                if message_condition:
                                    log_stream.warning(' ===> Datasets for variable ' + dset_key + ' is empty')
                                    message_condition = False
                            else:
                                log_stream.error(' ===> Collect dynamic datasets filename(s) failed!')
                                raise NotImplementedError('Type of folder or file name is not supported')

                        if dset_key not in dset_vars[dset_format]:
                            dset_vars[dset_format][dset_key] = {}
                            dset_vars[dset_format][dset_key] = file_path_list
                        else:
                            file_list_tmp = dset_vars[dset_format][dset_key]
                            file_list_tmp.extend(file_path_list)
                            dset_vars[dset_format][dset_key] = file_list_tmp

                        if dset_key not in dset_time[dset_format]:
                            dset_time[dset_format][dset_key] = file_time_list
                        else:
                            time_list_tmp = dset_time[dset_format][dset_key]
                            time_list_tmp.extend(file_time_list)
                            dset_time[dset_format][dset_key] = time_list_tmp

                        log_stream.info(' --------> Variable ' + dset_key + ' ... DONE')

                    log_stream.info(' -------> Type ' + dset_step_type + ' ... DONE')
                else:
                    log_stream.info(' -------> Type ' + dset_step_type + ' ... SKIPPED. Datasets is empty')

            dict_vars = dset_vars[dset_format]
            dict_time = dset_time[dset_format]

            df_vars = pd.DataFrame({'Time': datetime_idx_period})
            df_vars['File_Type'] = filetype_idx_period
            df_vars = df_vars.reset_index()
            df_vars = df_vars.set_index('Time')

            for (var_key, var_time), var_data in zip(dict_time.items(), dict_vars.values()):

                if dset_format == 'TimeSeries':
                    if isinstance(var_data, list):
                        var_data_tmp = self.column_sep.join(var_data)
                    else:
                        var_data_tmp = var_data

                    var_time_tmp = [datetime_idx_period[idx_group] for idx_group, idx_type in zip(
                        filegroup_idx_select, filetype_idx_select) if idx_type == 'OBS']

                    step_n = var_time_tmp.__len__()
                    var_data_tmp = [var_data_tmp] * step_n

                else:
                    var_data_tmp = var_data
                    var_time_tmp = var_time

                time_ts = pd.DatetimeIndex(var_time_tmp)
                var_ts = pd.Series(index=time_ts, data=var_data_tmp, name=var_key).fillna(value=pd.NA)
                df_vars[var_key] = var_ts

            ws_vars[dset_format] = df_vars

            log_stream.info(' ------> Collect ' + dset_format + ' source filename(s) ... DONE')

        ws_model = {}
        dset_model = {}
        dset_time = {}
        for dset_format, dset_workspace in dset_obj.items():

            log_stream.info(' ------> Collect ' + dset_format + ' model filename(s) ... ')

            dset_model[dset_format] = {}
            dset_time[dset_format] = {}

            dset_item = dset_workspace[self.model_tag]
            dset_source = dset_workspace[self.datasets_tag]

            folder_name_raw = dset_item[self.folder_name_tag]
            file_name_raw = dset_item[self.file_name_tag]

            file_var_lut = dset_lut[dset_format][self.model_tag]

            if dset_format == 'TimeSeries':

                filegroup_idx_select = [idx for type, idx in zip(
                    filetype_idx_period[filegroup_idx_start], filegroup_idx_start) if type in self.dset_list_type]
                filetype_idx_select = filetype_idx_period[filegroup_idx_select]

                filetype_idx_period_tmp = []
                datetime_idx_period_tmp = []
                for filegroup_idx_step in filegroup_idx_select:
                    datetime_idx_period_tmp.append(datetime_idx_period[filegroup_idx_step])
                    filetype_idx_period_tmp.append(filetype_idx_period[filegroup_idx_step])
                    break
                datetime_idx_period_tmp = pd.DatetimeIndex(datetime_idx_period_tmp)
            else:

                filegroup_idx_select = [idx for idx, type in enumerate(filetype_idx_period)
                                        if type in self.dset_list_group]

                filetype_idx_period_tmp = []
                datetime_idx_period_tmp = []
                for filegroup_idx_step in filegroup_idx_select:
                    datetime_idx_period_tmp.append(datetime_idx_period[filegroup_idx_step])
                    filetype_idx_period_tmp.append(filetype_idx_period[filegroup_idx_step])

            file_path_list = []
            file_time_list = []
            file_path_merged = []
            for datetime_idx_step in datetime_idx_period_tmp:
                datetime_step = datetime_idx_step.to_pydatetime()

                template_run_ref_step = deepcopy(template_run_ref)
                template_run_filled_step = deepcopy(template_run_filled)

                template_time_filled = dict.fromkeys(list(self.template_time.keys()), datetime_step)
                template_merge_filled = {**template_run_filled_step, **template_time_filled}

                template_merge_ref = {**template_run_ref_step, **self.template_time}

                if dset_format == 'Point':
                    template_merge_filled['dset_var_name_forcing_point'] = file_var_lut
                    if template_keys_extra is not None:
                        for template_key_extra in template_keys_extra:
                            template_merge_filled[template_key_extra] = None

                if dset_format == 'TimeSeries':
                    if template_run_extra is not None:
                        template_merge_filled = {**template_merge_filled, **template_run_extra}

                folder_name_tmp = fill_tags2string(folder_name_raw, template_merge_ref, template_merge_filled)
                file_name_tmp = fill_tags2string(file_name_raw, template_merge_ref, template_merge_filled)

                if isinstance(folder_name_tmp, list) and isinstance(file_name_tmp, list):
                    for folder_name_tmp_step, file_name_tmp_step in zip(folder_name_tmp, file_name_tmp):
                        file_path_tmp = os.path.join(folder_name_tmp_step, file_name_tmp_step)
                        if file_path_tmp not in file_path_list:
                            file_path_list.append(file_path_tmp)
                        if datetime_idx_step not in file_time_list:
                            file_time_list.append(datetime_idx_step)
                elif isinstance(folder_name_tmp, str) and isinstance(file_name_tmp, str):
                    file_path_list.append(os.path.join(folder_name_tmp, file_name_tmp))
                    file_time_list.append(datetime_idx_step)
                else:
                    log_stream.error(' ===> Collect dynamic model filename(s) failed!')
                    raise NotImplementedError('Type of folder or file name is not supported')

                if dset_format == 'Point':
                    if isinstance(file_path_list, list):
                        file_path_tmp = self.column_sep.join(file_path_list)
                        file_path_merged.append(file_path_tmp)
                        file_path_list = []
                    else:
                        file_path_merged = deepcopy(file_path_list)
                else:
                    file_path_merged = deepcopy(file_path_list)

            dset_model[dset_format][self.model_tag] = {}
            dset_model[dset_format][self.model_tag] = file_path_merged
            dset_time[dset_format][self.model_tag] = {}
            dset_time[dset_format][self.model_tag] = file_time_list

            dict_model = dset_model[dset_format]
            dict_time = dset_time[dset_format]

            df_model = pd.DataFrame({'Time': datetime_idx_period})
            df_model['File_Type'] = filetype_idx_period
            df_model = df_model.reset_index()
            df_model = df_model.set_index('Time')

            for (var_key, var_time), var_data in zip(dict_time.items(), dict_model.values()):

                if dset_format == 'TimeSeries':
                    if isinstance(var_data, list):
                        var_data_tmp = self.column_sep.join(var_data)
                    else:
                        var_data_tmp = var_data

                    var_time_tmp = [datetime_idx_period[idx_group] for idx_group, idx_type in zip(
                        filegroup_idx_select, filetype_idx_select) if idx_type == 'OBS']

                    step_n = var_time_tmp.__len__()
                    var_data_tmp = [var_data_tmp] * step_n
                else:
                    var_data_tmp = var_data
                    var_time_tmp = var_time

                time_ts = pd.DatetimeIndex(var_time_tmp)
                var_ts = pd.Series(index=time_ts, data=var_data_tmp, name=var_key).fillna(value=pd.NA)
                df_model[var_key] = var_ts

            ws_model[dset_format] = df_model

            log_stream.info(' ------> Collect ' + dset_format + ' model filename(s) ... DONE')

        return ws_vars, ws_model
# -------------------------------------------------------------------------------------
