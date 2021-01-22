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

import pandas as pd

from hmc.algorithm.io.lib_data_io_nc import read_data as read_data_nc
from hmc.algorithm.io.lib_data_io_ascii import read_data_point, read_data_time_series, read_state_point, \
    read_outcome_point, read_outcome_time_series
from hmc.algorithm.io.lib_data_io_generic import store_file
from hmc.algorithm.io.lib_data_geo_ascii import read_data_vector, read_data_grid
from hmc.algorithm.io.lib_data_geo_ascii import read_data_point_dam, read_data_point_intake, \
    read_data_point_section, write_data_point_section
from hmc.algorithm.io.lib_data_geo_shapefile import read_data_shapefile_section
from hmc.algorithm.io.lib_data_zip_gzip import unzip_filename


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
    def __init__(self, file_src_path, file_src_info, file_src_time, time_src_info, **kwargs):

        if isinstance(file_src_path, str):
            file_src_path = [file_src_path]

        file_src_tmp_raw = list(set(file_src_path))

        file_src_tmp_list = []
        for file_src_step in file_src_tmp_raw:
            if isinstance(file_src_step, str):
                file_src_tmp_list.append(file_src_step)

        if (file_src_tmp_list.__len__() > 1) and (file_src_tmp_list.__len__() != file_src_time.__len__()):
            log_stream.error(' ===> File(s) expected is less then time(s) expected.')
            raise IOError('Some files are not correctly defined. Check your settings!')

        self.file_src_info = file_src_info
        self.file_src_time = file_src_time
        self.file_zip_extension = zip_extension

        self.time_src_info = time_src_info

        self.column_sep = ';'

        if file_src_tmp_list.__len__() >= 1:
            if file_src_path[0].endswith(self.file_zip_extension):
                self.file_unzip_op = True
            else:
                self.file_unzip_op = False

            if self.file_unzip_op:
                file_src_path_list = []
                for file_src_path_step in file_src_tmp_list:
                    file_src_path_tmp = remove_zip_extension(file_src_path_step, self.file_zip_extension)
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
                    obj_var = None
                elif var_name == 'Joint':
                    obj_var = None
                elif var_name == 'Section':
                    obj_var = read_data_point_section(file_path)
                else:
                    log_stream.error(' ===> Point static variable is not valid in reading method')
                    raise IOError('Point variable name is not allowed')

            elif self.file_src_format == 'shapefile':
                if var_name == 'Section':
                    obj_var = read_data_shapefile_section(file_path)
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
                raise IOError('File not found')
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
                elif not self.file_unzip_op:
                    file_path = self.file_src_path
            elif tag_datatype == 'outcome':
                if self.file_unzip_op:
                    file_path = self.file_dest_path
                elif not self.file_unzip_op:
                    file_path = self.file_src_path
            else:
                log_stream.error(' ===> File dynamic type is not allowed! Check your datasets!')
                raise IOError('File type not allowed')

            if self.file_src_name is not None:
                file_var_name = self.file_src_name
            else:
                file_var_name = var_name

            # Info
            log_stream.info(' ---------> TimePeriod ' + str(var_time_start) + ' :: ' + str(var_time_end) + ' ... ')

            if self.file_src_format == 'netcdf':

                da_var, da_time, geo_x, geo_y = read_data_nc(file_path, var_name=file_var_name,
                                                             var_time_start=var_time_start, var_time_end=var_time_end)

                if da_var is not None:
                    if var_name == 'ALL':
                        obj_var = da_var
                    else:
                        obj_var = da_var.to_dataset(name=file_var_name)
                else:
                    obj_var = None

            elif self.file_src_format == 'ascii_point':

                if var_name == 'Discharge':

                    if tag_datatype == 'forcing':
                        file_columns_var = {0: 'ref', 1: 'section_discharge_obs', 2: 'section_tag'}
                        obj_var = read_data_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                  file_ancillary=var_static_info,
                                                  select_columns=['ref', 'section_discharge_obs'])
                    elif tag_datatype == 'outcome':
                        file_columns_var = {0: 'section_discharge_sim'}
                        obj_var = read_outcome_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                     file_ancillary=var_static_info)
                    else:
                        log_stream.error(' ===> File type point for discharge variable is not allowed!')
                        raise IOError('File type not allowed')

                elif var_name == 'DamV':

                    if tag_datatype == 'forcing':
                        file_columns_var = {0: 'ref', 1: 'dam_volume_obs', 2: 'dam_volume_max'}
                        obj_var = read_data_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                  file_ancillary=var_static_info)
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
                        obj_var = read_data_point(file_path, self.file_src_time, file_columns=file_columns_var,
                                                  file_ancillary=var_static_info)
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
                    var_columns_list = var_args['plant_name_list']
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
    def __init__(self, file_dst_path, file_dst_info, file_dst_time, time_dst_info):
        super(DSetWriter, self).__init__(file_dst_path, file_dst_info, file_dst_time, time_dst_info)
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

            log_stream.error(' ===> ASCII grid format is not valid in writing method')
            raise IOError('File format is not allowed')

        elif self.file_src_format == 'ascii_point':

            if var_name == 'Section':
                write_data_point_section(file_path, var_data)
                # Call method from super-class
                obj_var = self.read_filename_static(var_name)
            else:
                log_stream.error(' ===> Point static variable is not valid in writing method')
                raise IOError('Point variable name is not allowed')

        else:
            log_stream.error(' ===> File static type is not allowed in writing method! Check your datasets!')
            raise IOError('File type not allowed')

        # Check mandatory variable status
        if obj_var is None:
            if self.file_src_mandatory:
                log_stream.error(' ===> File static ' + file_path + ' is mandatory! Execution exit.')
                log_stream.info(' ------> Write variable ' + var_name + ' ... FAILED')
                raise IOError('File not found')
            else:
                log_stream.warning(' ===> File static ' + file_path + ' is ancillary! Execution continue.')
                log_stream.info(' ------> Write variable ' + var_name + ' ... SKIPPED')
        else:
            log_stream.info(' ------> Write variable ' + var_name + ' ... DONE')

        return obj_var

# -------------------------------------------------------------------------------------
