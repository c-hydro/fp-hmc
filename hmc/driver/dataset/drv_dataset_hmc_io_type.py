"""
Class Features

Name:          drv_dataset_hmc_io_type
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os

import numpy as np
import pandas as pd

from copy import deepcopy

from hmc.algorithm.io.lib_data_io_nc import read_data as read_data_nc
from hmc.algorithm.io.lib_data_io_tiff import read_data as read_data_tiff

from hmc.algorithm.io.lib_data_io_ascii import read_data_point, read_data_time_series, read_state_point, \
    read_outcome_point, read_outcome_time_series
from hmc.algorithm.io.lib_data_io_generic import store_file
from hmc.algorithm.io.lib_data_geo_ascii import read_data_vector, read_data_grid, write_data_grid
from hmc.algorithm.io.lib_data_geo_ascii import read_data_point_dam, read_data_point_intake, \
    read_data_point_joint, read_data_point_lake, \
    read_data_point_section, write_data_point_section, write_data_point_undefined
from hmc.algorithm.io.lib_data_geo_shapefile import read_data_shapefile_section
from hmc.algorithm.io.lib_data_zip_gzip import unzip_filename

from hmc.algorithm.utils.lib_utils_variable import convert_fx_interface
from hmc.algorithm.utils.lib_utils_geo import compute_cell_area
from hmc.algorithm.utils.lib_utils_system import delete_file

from hmc.algorithm.utils.lib_utils_zip import remove_zip_extension
from hmc.algorithm.default.lib_default_args import logger_name, zip_extension

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to read datasets
class DSetReader:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, file_src_path, file_src_info, file_src_time, time_src_info,
                 file_tmp_path=None, file_tmp_clean=False, **kwargs):

        if isinstance(file_src_path, str):
            file_src_path = [file_src_path]

        if 'file_src_mandatory' in kwargs:
            file_src_mandatory = kwargs['file_src_mandatory']
        else:
            file_src_mandatory = False

        file_src_tmp_raw = list(set(file_src_path))

        file_src_tmp_list = []
        for file_src_step in file_src_tmp_raw:
            if isinstance(file_src_step, str):
                file_src_tmp_list.append(file_src_step)

        # Method to check the filename(s) availability according to the mandatory flag
        self.search_filename(file_src_tmp_list, file_mandatory_flag=file_src_mandatory)

        if (file_src_tmp_list.__len__() > 1) and (file_src_tmp_list.__len__() != file_src_time.__len__()):

            file_src_tmp_list = sorted(file_src_tmp_list)
            file_src_date_list = sorted(list(set(list(file_src_time.date))))

            if file_src_tmp_list.__len__() == file_src_date_list.__len__():
                file_src_filled_list = []
                for file_src_date_step, file_src_tmp_step in zip(file_src_date_list, file_src_tmp_list):
                    file_select_step = file_src_time[file_src_time.date == file_src_date_step]
                    file_src_filled_step = [file_src_tmp_step] * file_select_step.__len__()
                    file_src_filled_list.extend(file_src_filled_step)
                file_src_tmp_list = deepcopy(file_src_filled_list)
            else:
                log_stream.error(' ===> File(s) expected are not equal to time steps expected.')
                raise IOError('Files does not match time steps length. Check your settings!')

        self.file_src_info = file_src_info
        self.file_src_time = file_src_time
        self.file_zip_extension = zip_extension

        self.time_src_info = time_src_info

        self.column_sep = ';'

        if file_src_tmp_list.__len__() >= 1:
            if file_src_path[0].endswith(self.file_zip_extension):
                self.file_unzip_op = True
                self.file_unzip_delete = file_tmp_clean
            else:
                self.file_unzip_op = False
                self.file_unzip_delete = False

            if self.file_unzip_op:
                file_src_path_list = []
                for file_src_path_step in file_src_tmp_list:
                    file_src_path_tmp = remove_zip_extension(
                        file_src_path_step, file_path_tmp=file_tmp_path, zip_extension_template=self.file_zip_extension)
                    file_src_path_list.append(file_src_path_tmp)
                self.file_src_path = sorted(file_src_tmp_list)
                self.file_dest_path = sorted(file_src_path_list)
                self.unzip_filename()
            else:

                if self.column_sep in file_src_tmp_list[0]:
                    self.file_src_path = file_src_tmp_list[0].split(self.column_sep)
                else:
                    self.file_src_path = sorted(file_src_tmp_list)
                self.file_dest_path = None

        else:
            self.file_src_path = None
            self.file_dest_path = None
            self.file_unzip_op = None

        if 'var_dset' in list(file_src_info.keys()):
            self.file_src_name = file_src_info['var_dset']
        else:
            self.file_src_name = None

        if 'var_format' in list(file_src_info.keys()):
            self.file_src_format = file_src_info['var_format']
        elif 'var_format' in list(kwargs.keys()):
            self.file_src_format = kwargs['var_format']
        else:
            self.file_src_format = None

        if 'var_limits' in list(file_src_info.keys()):
            self.file_src_limits = file_src_info['var_limits']
        else:
            self.file_src_limits = None

        if 'var_operation' in list(file_src_info.keys()):
            self.file_src_operation = file_src_info['var_operation']
        else:
            self.file_src_operation = None

        if 'var_mandatory' in list(file_src_info.keys()):
            self.file_src_mandatory = file_src_info['var_mandatory']
        else:
            self.file_src_mandatory = None

        if 'var_check' in list(file_src_info.keys()):
            self.file_src_check = file_src_info['var_check']
        else:
            self.file_src_check = None

        if 'var_filter' in list(file_src_info.keys()):
            self.file_src_filter = file_src_info['var_filter']
        else:
            self.file_src_filter = None

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to search file name(s)
    @staticmethod
    def search_filename(file_name_list, file_mandatory_flag=False):

        if not isinstance(file_name_list, list):
            file_name_list = [file_name_list]

        file_found_list, file_not_found_list = None, None
        for file_name_step in file_name_list:
            if file_name_step:
                if os.path.exists(file_name_step):
                    if file_found_list is None:
                        file_found_list = []
                    file_found_list.append(file_name_step)
                else:
                    if file_not_found_list is None:
                        file_not_found_list = []
                    file_not_found_list.append(file_name_step)

        if file_mandatory_flag:
            if file_not_found_list is not None:
                log_stream.error(' ===> The following filename(s) with "mandatory_flag=True" '
                                 'is/are not available in the filesystem: ')
                for file_not_found_step in file_not_found_list:
                    log_stream.error(' ===> File: ' + file_not_found_step)
                raise FileNotFoundError('All files are mandatory to correctly run the algorithm')
        if not file_mandatory_flag:
            if file_not_found_list is not None:
                log_stream.warning(' ===> Some/all filename(s) with "mandatory_flag=False" '
                                   'is/are not available in the filesystem')

        if file_not_found_list is None and file_found_list is None:
            log_stream.warning(' ===> Filename(s) for this datasets is/are not selected. '
                               'Run will not use this datasets')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to unzip file name
    def unzip_filename(self):

        unzip_message = False
        for file_src_path_step, file_dest_path_step in zip(self.file_src_path, self.file_dest_path):
            if os.path.exists(file_src_path_step):
                if not os.path.exists(file_dest_path_step):
                    unzip_filename(file_src_path_step, file_dest_path_step)
            else:
                unzip_message = True
        if unzip_message:
            log_stream.warning(' ===> Some/All filenames are not available! Unzipping failed!')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write filename for static datasets
    @staticmethod
    def write_filename_undefined(file_path, var_name):

        # Write an empty point static file
        if var_name in ['Dam', 'Intake', 'Lake', 'Joint']:
            write_data_point_undefined(file_path)
            log_stream.warning(' ===> File static for variable ' + var_name + ' is initialized by constants value')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read filename for static datasets
    def read_filename_static(self, var_name):

        # Info
        log_stream.info(' ------> Read variable ' + var_name + ' ... ')

        if self.file_unzip_op:
            file_path = self.file_dest_path
        else:
            file_path = self.file_src_path

        if isinstance(file_path, list):
            file_path = file_path[0]

        if os.path.exists(file_path):

            if self.file_src_format == 'ascii_grid':

                if var_name == 'Vegetation_IA':
                    obj_var = read_data_vector(file_path)
                else:
                    obj_var = read_data_grid(file_path)

            elif self.file_src_format == 'ascii_point':

                if var_name == 'Dam':
                    obj_var = read_data_point_dam(file_path)
                elif var_name == 'Intake':
                    obj_var = read_data_point_intake(file_path)
                elif var_name == 'Lake':
                    obj_var = read_data_point_lake(file_path)
                elif var_name == 'Joint':
                    obj_var = read_data_point_joint(file_path)
                elif var_name == 'Section':
                    obj_var = read_data_point_section(file_path)
                else:
                    log_stream.error(' ===> Point static variable is not valid in reading method')
                    raise IOError('Point variable name is not allowed')

            elif self.file_src_format == 'shapefile':
                if var_name == 'Section':
                    obj_var = read_data_shapefile_section(
                        file_path, row_filter_type=self.file_src_filter)
                else:
                    log_stream.error(' ===> Shapefile static variable is not valid in reading method')
                    raise IOError('Shapefile variable name is not allowed')
            else:
                log_stream.error(' ===> File static type is not allowed in reading method! Check your datasets!')
                raise IOError('File type not allowed')

        else:

            log_stream.warning(' ===> File static for variable ' + var_name + ' is not found in reading method!')
            log_stream.warning(' ===> Filename: ' + file_path)

            obj_var = None

        # Check mandatory variable status
        if obj_var is None:
            if self.file_src_mandatory:
                log_stream.error(' ===> File static ' + file_path + ' is mandatory! Execution exit.')
                log_stream.info(' ------> Read variable ' + var_name + ' ... FAILED')
                raise IOError('File not found or datasets are undefined. Check your input or settings!')
            else:
                log_stream.warning(' ===> File static ' + file_path + ' is ancillary! Execution continue.')
                log_stream.info(' ------> Read variable ' + var_name + ' ... SKIPPED')
        else:
            log_stream.info(' ------> Read variable ' + var_name + ' ... DONE')

        return obj_var

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to read dynamic filename
    def read_filename_dynamic(self, var_name, var_args, var_time_start=None, var_time_end=None, var_static_info=None,
                              tag_datatype='forcing'):

        # Info
        log_stream.info(' --------> Variable ' + var_name + ' ... ')

        if self.file_unzip_op is not None:

            if tag_datatype == 'forcing':
                if self.file_unzip_op:
                    file_path = self.file_dest_path
                    file_unzip_delete = self.file_unzip_delete
                elif not self.file_unzip_op:
                    file_path = self.file_src_path
                    file_unzip_delete = self.file_unzip_delete
            elif tag_datatype == 'outcome':
                if self.file_unzip_op:
                    file_path = self.file_dest_path
                    file_unzip_delete = False
                elif not self.file_unzip_op:
                    file_path = self.file_src_path
                    file_unzip_delete = False
            else:
                log_stream.error(' ===> File dynamic type is not allowed! Check your datasets!')
                raise IOError('File type not allowed')

            if isinstance(file_path, list):
                for id_path, step_path in enumerate(file_path):
                    if step_path == '':
                        file_path[id_path] = None
            else:
                log_stream.error(' ===> File dynamic path is in wrong format!')
                raise NotImplementedError('File path format not implemented yet')

            if self.file_src_name is not None:
                file_var_name = self.file_src_name
            else:
                file_var_name = var_name

            # Info
            log_stream.info(' ---------> TimePeriod ' + str(var_time_start) + ' :: ' + str(var_time_end) + ' ... ')

            if self.file_src_format == 'netcdf':

                da_var, da_time, geo_x, geo_y = read_data_nc(
                    file_path, var_name=file_var_name, var_time_start=var_time_start, var_time_end=var_time_end,
                    coord_name_time='time', coord_name_geo_x='Longitude', coord_name_geo_y='Latitude')

                if da_var is not None:
                    if var_name == 'ALL':
                        obj_var = da_var
                    else:
                        obj_var = da_var.to_dataset(name=file_var_name)
                else:
                    obj_var = None

            elif self.file_src_format == 'tiff':

                da_var, da_time, geo_x, geo_y = read_data_tiff(file_path, var_name=file_var_name,
                                                               var_time_start=var_time_start, var_time_end=var_time_end)

                if da_var is not None:
                    obj_var = da_var.to_dataset(name=file_var_name)
                else:
                    obj_var = None

            elif self.file_src_format == 'ascii_point':

                if var_name == 'Discharge':

                    if tag_datatype == 'forcing':
                        file_columns_var = {0: 'ref', 1: 'section_discharge_obs', 2: 'section_tag'}
                        file_columns_lut = {'section_tag': 'ref'}
                        obj_var = read_data_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                  file_ancillary=var_static_info,
                                                  file_lut=file_columns_lut,
                                                  select_columns=['ref', 'section_discharge_obs'])
                    elif tag_datatype == 'outcome':
                        file_columns_var = {0: 'section_discharge_sim'}
                        file_columns_remap = {'section_baseflow': {'limits': [0, None], 'type': 'constant'}}
                        obj_var = read_outcome_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                     file_map=file_columns_remap,
                                                     file_ancillary=var_static_info)
                    else:
                        log_stream.error(' ===> File type point for discharge variable is not allowed!')
                        raise IOError('File type not allowed')

                elif var_name == 'DamV':

                    if tag_datatype == 'forcing':
                        file_columns_var = {0: 'ref', 1: 'dam_volume_obs', 2: 'dam_volume_max'}
                        file_columns_lut = None
                        obj_var = read_data_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                  file_ancillary=var_static_info, file_lut=file_columns_lut)
                    elif tag_datatype == 'outcome':
                        file_columns_var = {0: 'dam_volume_sim'}
                        obj_var = read_outcome_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                     file_ancillary=var_static_info)
                    else:
                        log_stream.error(' ===> File type point for dam volume variable is not allowed!')
                        raise IOError('File type not allowed')

                elif var_name == 'DamL':

                    if tag_datatype == 'forcing':
                        file_columns_var = {0: 'ref', 1: 'dam_level_obs', 2: 'dam_level_max'}
                        file_columns_lut = None
                        obj_var = read_data_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                  file_ancillary=var_static_info, file_lut=file_columns_lut)
                    elif tag_datatype == 'outcome':
                        file_columns_var = {0: 'dam_level_sim'}
                        obj_var = read_outcome_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                     file_ancillary=var_static_info)
                    else:
                        log_stream.error(' ===> File type point for dam level variable is not allowed!')
                        raise IOError('File type not allowed')

                elif var_name == 'VarAnalysis':

                    if tag_datatype == 'outcome':
                        obj_var = None
                    else:
                        log_stream.error(' ===> File type point for var analysis variable is not allowed!')
                        raise IOError('File type not allowed')

                elif var_name == 'ALL':
                    file_columns_var = {0: 'dam_index', 1: 'dam_code', 2: 'dam_volume_max', 3: 'dam_volume_sim'}
                    list_columns_excluded = ['dam_index', 'dam_code', 'dam_volume_max']
                    if var_args['plant_name_list'] is not None:
                        if var_args['lake_name_list'] is not None:
                            # if there are both plants and lakes in the restart both should be present
                            var_columns_list = var_args['plant_name_list'] + var_args['lake_name_list']
                        else:
                            # if there are only plants
                            var_columns_list = var_args['plant_name_list']
                    elif var_args['lake_name_list'] is not None:
                        # if there are only lakes
                        var_columns_list = var_args['lake_name_list']
                    else:
                        # if there are neither lakes nor plants
                        var_columns_list = []

                    # releases related to intakes are not in the restart point file, remove them from check list
                    if var_args['release_name_list'] is not None:
                        var_columns_list = [i for i in var_columns_list if i not in var_args['release_name_list']]

                    obj_name = 'DamV'
                    obj_var = read_state_point(file_path, self.file_src_time, var_name=obj_name,
                                               file_time_start=var_time_start, file_time_end=var_time_end,
                                               file_columns_type=file_columns_var, file_columns_name=var_columns_list,
                                               list_columns_excluded=list_columns_excluded)
                else:
                    log_stream.error(' ===> Point dynamic variable is not valid')
                    raise IOError('Point variable name is not allowed')

                da_time = None
                geo_x = None
                geo_y = None

            elif self.file_src_format == 'ascii_time_series':

                if tag_datatype == 'forcing':
                    if var_name == 'DamQ':
                        file_columns_var = {0: 'dam_discharge_obs'}
                    elif var_name == 'IntakeQ':
                        file_columns_var = {0: 'intake_discharge_obs'}
                    else:
                        log_stream.error(' ===> TimeSeries dynamic variable is not valid')
                        raise IOError('TimeSeries variable name is not allowed')

                    var_columns_list = var_args['plant_name_list']

                    time_obs_delta = self.time_src_info['time_observed_delta']
                    time_obs_freq = pd.Timedelta(pd.offsets.Second(time_obs_delta)).resolution_string

                    obj_var = read_data_time_series(
                        file_path, self.file_src_time,
                        file_columns_type=file_columns_var, file_columns_name=var_columns_list,
                        file_time_start=var_time_start, file_time_end=var_time_end,
                        file_time_frequency=time_obs_freq)
                    da_time = None
                    geo_x = None
                    geo_y = None

                elif tag_datatype == 'outcome':

                    if var_name == 'Discharge':
                        file_columns_var = {0: 'time', 0: 'section_discharge_sim'}
                    elif var_name == 'DamV':
                        file_columns_var = {0: 'time', 0: 'dam_volume_sim'}
                    elif var_name == 'DamL':
                        file_columns_var = {0: 'time', 0: 'dam_level_sim'}
                    elif var_name == 'VarAnalysis':
                        file_columns_var = None
                    else:
                        log_stream.error(' ===> TimeSeries dynamic variable is not valid')
                        raise IOError('TimeSeries variable name is not allowed')

                    if var_static_info:
                        var_columns_list = list(var_static_info.keys())
                    else:
                        var_columns_list = None

                    time_obs_delta = self.time_src_info['time_observed_delta']
                    time_obs_freq = pd.Timedelta(pd.offsets.Second(time_obs_delta)).resolution_string

                    obj_var = None
                    da_time = None
                    geo_x = None
                    geo_y = None

                else:
                    log_stream.error(' ===> File type point for var analysis variable is not allowed!')
                    raise IOError('File type not allowed')

            else:
                log_stream.error(' ===> File dynamic type is not allowed! Check your datasets!')
                raise IOError('File type not allowed')

            # Delete temporary file (generally unzipped nc files)
            if file_unzip_delete:
                if isinstance(file_path, str):
                    file_path = [file_path]
                for file_step in file_path:
                    delete_file(file_step)

            # Info
            log_stream.info(' ---------> TimePeriod ' + str(var_time_start) + ' :: ' + str(var_time_end) + ' ... DONE')

        else:
            log_stream.warning(' ===> Some/All filenames are not available!')
            obj_var = None
            da_time = None
            geo_x = None
            geo_y = None

        # Info
        log_stream.info(' --------> Variable ' + var_name + ' ... DONE')

        return obj_var, da_time, geo_x, geo_y
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Class to write datasets
class DSetWriter(DSetReader):

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, file_dst_path, file_dst_info, file_dst_time, time_dst_info, file_tmp_path, file_tmp_clean, ):
        super(DSetWriter, self).__init__(file_dst_path, file_dst_info, file_dst_time, time_dst_info,
                                         file_tmp_path, file_tmp_clean)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write filename for static datasets
    def write_filename_static(self, var_name, var_data):

        # Info
        log_stream.info(' ------> Write variable ' + var_name + ' ... ')

        file_path = self.file_src_path

        if isinstance(file_path, list):
            file_path = file_path[0]

        if os.path.exists(file_path):
            file_path_old = store_file(file_path, file_max=1)

        if self.file_src_format == 'ascii_grid':

            if var_name == 'Longitude' or var_name == 'Latitude':

                if var_name == 'Longitude':
                    lons_data = np.float32(var_data['longitude'])
                    write_data_grid(file_path, lons_data, file_ancillary=var_data)
                elif var_name == 'Latitude':
                    lats_data = np.float32(var_data['latitude'])
                    write_data_grid(file_path, lats_data, file_ancillary=var_data)

            elif var_name == 'Cell_Area':
                call_area_data = np.float32(var_data['cell_area'])
                write_data_grid(file_path, call_area_data, file_ancillary=var_data)
            else:
                log_stream.error(' ===> Grid static variable "' + var_name + '" is not valid in writing method')
                raise IOError('Grid variable name is not allowed')

            # Call method from super-class
            obj_var = self.read_filename_static(file_path)

        elif self.file_src_format == 'ascii_point':

            if var_name == 'Section':
                write_data_point_section(file_path, var_data)
                # Call method from super-class
                obj_var = self.read_filename_static(var_name)
            else:
                log_stream.error(' ===> Point static variable "' + var_name + '" is not valid in writing method')
                raise IOError('Point variable name is not allowed')

        else:
            log_stream.error(' ===> File static type is not allowed in writing method! Check your datasets!')
            raise IOError('File type not allowed')

        # Check mandatory variable status
        if obj_var is None:
            if self.file_src_mandatory:
                log_stream.error(' ===> File static ' + file_path + ' is mandatory! Execution exit.')
                log_stream.info(' ------> Write variable "' + var_name + '" ... FAILED')
                raise IOError('File not found')
            else:
                log_stream.warning(' ===> File static "' + file_path + '" is ancillary! Execution continue.')
                log_stream.info(' ------> Write variable "' + var_name + '" ... SKIPPED')
        else:
            log_stream.info(' ------> Write variable ' + var_name + ' ... DONE')

        return obj_var

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Class to compose datasets
class DSetComposer(DSetWriter):

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, file_dst_path, file_dst_info, file_dst_time, time_dst_info,
                 file_tmp_path, file_tmp_clean):

        super(DSetComposer, self).__init__(file_dst_path, file_dst_info, file_dst_time, time_dst_info,
                                           file_tmp_path, file_tmp_clean)

        self.var_info = file_dst_info

        self.tag_var_file_units = 'var_file_units'
        self.tag_var_file_limits = 'var_file_limits'

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to check data units (with constants reference)
    def validate_data_units(self, var_name, var_data, var_info_default):

        # Info
        log_stream.info(' ---------> Validate ' + var_name + ' units ... ')

        # Get dataset info
        var_info = self.var_info

        var_info_valid = deepcopy(var_info)
        var_data_valid = deepcopy(var_data)
        if var_info_default is not None:

            if self.tag_var_file_units in list(var_info_default.keys()):
                var_units_default = var_info_default[self.tag_var_file_units]
            else:
                var_units_default = None
            if 'var_units' in list(var_info.keys()):
                var_units = var_info['var_units']
            else:
                var_units = None

            if self.tag_var_file_limits in list(var_info_default.keys()):
                var_limits_default = var_info_default[self.tag_var_file_limits]
            else:
                var_limits_default = None

            if (var_units is not None) and (var_units_default is not None):

                if var_units_default == var_units:
                    log_stream.info(' ---------> Validate ' +
                                    var_name + ' units ... DONE. Default units [' + var_units_default +
                                    '] and datasets units [' + var_units + '] are equal')
                elif var_units_default != var_units:

                    if var_name == 'AirTemperature':

                        var_data_valid, var_info_valid = convert_fx_interface(var_name, var_data, var_info,
                                                                              var_units, var_units_default,
                                                                              var_limits_default)
                    else:
                        log_stream.info(' ---------> Validate ' + var_name + ' units ... FAILED')
                        log_stream.error(' ===> Default units [' + var_units +
                                         '] and datasets units [' + var_units + '] are different. \n'
                                         'Method to convert units is not provided. ')
                        raise NotImplementedError('Case not implemented yet')

                else:
                    log_stream.info(' ---------> Validate ' + var_name + ' units ... FAILED')
                    log_stream.error(' ===> Variable units and constants units are found in wrong format')
                    raise NotImplementedError('Case not implemented yet')

            elif (var_units is None) and (var_units_default is None):
                log_stream.info(' ---------> Validate ' +
                                var_name + ' units ... SKIPPED. Default and dataset units are defined by [None]')
                log_stream.warning(' ===> Set units in "lib_default_variables.py" constants file or in the settings file')
            elif (var_units is not None) and (var_units_default is None):
                log_stream.info(' ---------> Validate ' +
                                var_name + ' units ... SKIPPED. Default units are [None]'
                                ' and datasets units are [' + var_units + ']. Use datasets units in the variable obj')
                log_stream.warning(' ===> Set units in "lib_default_variables.py" constants file')
            elif (var_units is None) and (var_units_default is not None):
                log_stream.info(' ---------> Validate ' +
                                var_name + ' units ... SKIPPED. Default units are [' + var_units_default +
                                '] and datasets units are [None]. Use constants units in the variable obj')
                log_stream.warning(' ===> Set units in the settings file')
            else:
                log_stream.info(' ---------> Validate ' + var_name + ' units ... FAILED')
                log_stream.error(' ===> Variable units and constants units are found in wrong type')
                raise NotImplementedError('Case not implemented yet')

        else:
            log_stream.info(' ---------> Validate ' + var_name + ' units ... SKIPPED')
            log_stream.warning(' ===> Variable "' + var_name +
                               '" is not defined in constants dictionary. Add it in the "lib_default_variables.py"')

        # Update class variable(s)
        self.var_info = var_info_valid

        return var_data_valid

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to write filename for static datasets
    def compute_data_static(self, var_name, var_data):

        # Info
        log_stream.info(' ------> Compute variable ' + var_name + ' ... ')

        file_path = self.file_src_path

        if isinstance(file_path, list):
            file_path = file_path[0]

        if self.file_src_format == 'ascii_grid':

            if var_name == 'Cell_Area':

                var_data['cell_area'] = compute_cell_area(var_data['longitude'], var_data['latitude'],
                                                          var_data['res_lon'], var_data['res_lat'])

                # Call methods from super-class
                self.write_filename_static(var_name, var_data)
                # Call methods from super-class
                obj_var = self.read_filename_static(file_path)

            else:
                log_stream.error(' ===> Grid static variable "' + var_name + '" is not valid in computing method')
                raise IOError('Grid variable name is not allowed')

        elif self.file_src_format == 'ascii_point':

            log_stream.error(' ===> Point static variable "' + var_name + '" is not valid in computing method')
            raise IOError('Point variable name is not allowed')

        else:
            log_stream.error(' ===> File static type is not allowed in computing method! Check your datasets!')
            raise IOError('File type not allowed')

        # Check mandatory variable status
        if obj_var is None:
            if self.file_src_mandatory:
                log_stream.error(' ===> File static ' + file_path + ' is mandatory! Execution exit.')
                log_stream.info(' ------> Compute variable "' + var_name + '" ... FAILED')
                raise IOError('File not found')
            else:
                log_stream.warning(' ===> File static "' + file_path + '" is ancillary! Execution continue.')
                log_stream.info(' ------> Compute variable "' + var_name + '" ... SKIPPED')
        else:
            log_stream.info(' ------> Compute variable ' + var_name + ' ... DONE')

        return obj_var

# -------------------------------------------------------------------------------------
