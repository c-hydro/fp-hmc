"""
Class Features

Name:          drv_configuration_hmc_args
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os

from hmc.algorithm.io.lib_data_io_json import read_file_json
from hmc.algorithm.utils.lib_utils_time import get_time
from hmc.algorithm.utils.lib_utils_dict import get_dict_value, delete_dict_keys

from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to configure arguments
class ModelArgs:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, file_algorithm, file_datasets, time,
                 tag_general_info='General_Info', tag_run_info='Run_Info', tag_time_info='Time_Info',
                 tag_hmc_info='HMC_Info', tag_geosystem_info='GeoSystem_Info', tag_template='Template',
                 **kwargs):

        # Get argument(s)
        self.file_algorithm = file_algorithm
        self.file_datasets = file_datasets
        self.time = time

        self.tag_general_info = tag_general_info
        self.tag_run_info = tag_run_info
        self.tag_time_info = tag_time_info
        self.tag_hmc_info = tag_hmc_info
        self.tag_geosystem_info = tag_geosystem_info
        self.tag_template = tag_template

        self.tag_template_run = 'run'
        self.tag_template_time = 'time'
        self.tag_template_dset_static = 'dset_static'
        self.tag_template_dset_dynamic_forcing = 'dset_dynamic_forcing'
        self.tag_template_dset_dynamic_outcome = 'dset_dynamic_outcome'
        self.tag_template_dset_dynamic_obs = 'dset_dynamic_obs'

        self.obj_keys_excluded = ['__comment', '_comment', '__comment__']

        # Get algorithm info
        self.obj_algorithm = self.get_file_algorithm(self.file_algorithm)
        # Get datasets info
        tmp_datasets = self.get_file_datasets(self.file_datasets)
        self.obj_datasets = delete_dict_keys(tmp_datasets, self.obj_keys_excluded)

        # Get time info
        self.obj_time_arg = get_time(self.time)

        obj_template_ref = None
        for obj_key, obj_value in self.obj_algorithm.items():
            if obj_key == self.tag_template:
                obj_template_ref = obj_value
                break
        self.obj_algorithm.pop(self.tag_template, None)

        self.obj_template_run_ref = obj_template_ref[self.tag_template_run]
        self.obj_template_time_ref = obj_template_ref[self.tag_template_time]
        self.obj_template_dset_static_ref = obj_template_ref[self.tag_template_dset_static]
        self.obj_template_dset_dynamic_ref = obj_template_ref[self.tag_template_dset_dynamic_forcing]
        self.obj_template_dset_outcome_ref = obj_template_ref[self.tag_template_dset_dynamic_outcome]
        self.obj_template_dset_obs_ref = obj_template_ref[self.tag_template_dset_dynamic_obs]

        obj_template_run_raw = {}
        for obj_key, obj_value in self.obj_template_run_ref.items():
            obj_tmp = get_dict_value(self.obj_algorithm, obj_key, [])
            if obj_tmp.__len__() > 0:
                obj_found = obj_tmp[0]
                obj_template_run_raw[obj_key] = obj_found
            else:
                log_stream.warning(' ===> Template key ' + obj_key + ' is not found in algorithm file settings!')
        self.obj_template_run_raw = obj_template_run_raw

        if tag_general_info in self.obj_algorithm:
            obj_general_info = self.obj_algorithm[tag_general_info]
        else:
            log_stream.error(' ===> General Info is not callable! Check your algorithm file!')
            raise ValueError('Value not valid')
        if tag_run_info in self.obj_algorithm:
            obj_run_info = self.obj_algorithm[tag_run_info]
        else:
            log_stream.error(' ===> Run Info is not callable! Check your algorithm file!')
            raise ValueError('Value not valid')
        if tag_time_info in self.obj_algorithm:
            obj_time_info = self.obj_algorithm[tag_time_info]
        else:
            log_stream.error(' ===> Time Info is not callable! Check your algorithm file!')
            raise ValueError('Value not valid')
        if tag_hmc_info in self.obj_algorithm:
            obj_hmc_info = self.obj_algorithm[tag_hmc_info]
        else:
            log_stream.error(' ===> HMC Info is not callable! Check your algorithm file!')
            raise ValueError('Value not valid')
        if tag_geosystem_info in self.obj_algorithm:
            obj_geosystem_info = self.obj_algorithm[tag_geosystem_info]
        else:
            log_stream.error(' ===> GeoSystem Info is not callable! Check your algorithm file!')
            raise ValueError('Value not valid')

        self.obj_general_info_ref = obj_general_info
        self.obj_run_info_ref = obj_run_info
        self.obj_time_info_ref = obj_time_info
        self.obj_hmc_info_ref = obj_hmc_info
        self.obj_geosystem_info_ref = obj_geosystem_info

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get file algorithm
    @staticmethod
    def get_file_algorithm(file_name):
        if os.path.exists(file_name):
            file_obj = read_file_json(file_name)
        else:
            log_stream.error(' ===> File algorithm is not available! Check your arguments!')
            raise IOError(" File not available.")
        return file_obj
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get file algorithm
    @staticmethod
    def get_file_datasets(file_name):
        if os.path.exists(file_name):
            file_obj = read_file_json(file_name)
        else:
            log_stream.error(' ===> File datasets is not available! Check your arguments!')
            raise IOError(" File not available.")
        return file_obj

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
