"""
Class Features

Name:          drv_configuration_hmc_namelist
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20241126'
Version:       '4.0.0'
"""

#######################################################################################
# Library
import logging

from copy import deepcopy

from hmc.algorithm.utils.lib_utils_time import parse_timefrequency_to_timeparts, convert_freqstr_to_freqsecs
from hmc.algorithm.utils.lib_utils_string import fill_tags2string
from hmc.algorithm.utils.lib_utils_dict import get_dict_value, get_dict_nested_value
from hmc.algorithm.namelist.lib_namelist import convert_template_date

from hmc.algorithm.default.lib_default_namelist import structure_namelist_default, link_namelist_default
from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to configure namelist
class ModelNamelist:

    # -------------------------------------------------------------------------------------
    # Method class initialization
    def __init__(self, obj_algorithm, obj_datasets,
                 key_namelist='namelist', filename_namelist=None, structure_namelist=None, **kwargs):

        self.obj_algorithm = obj_algorithm
        self.obj_datasets = obj_datasets

        if filename_namelist is None:
            filename_namelist = get_dict_value(obj_algorithm, key_namelist, [])[0]

        if structure_namelist is None:
            structure_namelist = structure_namelist_default

        self.filename_namelist_raw = filename_namelist
        self.structure_namelist_raw = structure_namelist
        self.link_namelist_raw = link_namelist_default

        self.line_indent = 4 * ' '

        self.lut_dt = {'iDtData_Forcing': 'DataForcing', 'iDtData_Updating': 'DataUpdating',
                       'iDtData_Output_Gridded': 'DataOutcome', 'iDtData_Output_Point': 'DataOutcome',
                       'iDtData_State_Gridded': 'DataState', 'iDtData_State_Point': 'DataState'}

        self.defined_dt = self.search_dt(self.lut_dt)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to search datasets frequency
    def search_dt(self, lut_dt, key_dt='hmc_file_frequency'):

        obj_datasets = self.obj_datasets

        obj_dt = {}
        for lut_key, lut_value in lut_dt.items():

            if lut_value in list(obj_datasets.keys()):
                obj_structure = obj_datasets[lut_value]

                if isinstance(obj_structure, dict):
                    collections_dt = []
                    for dataset_key, fields_structure in obj_structure.items():
                        if isinstance(fields_structure, dict):
                            list_dt = get_dict_value(fields_structure, key_dt, [])
                            if list_dt.__len__() > 0:
                                digits_dt, alpha_dt = parse_timefrequency_to_timeparts(list_dt)
                                num_dt = convert_freqstr_to_freqsecs(digits_dt, alpha_dt)
                                collections_dt.append(num_dt)

                    if collections_dt.__len__() > 0:

                        collections_dt = list(set(collections_dt))
                        if collections_dt.__len__() > 1:
                            value_dt = min(collections_dt)
                            log_stream.warning(' ===> Datasets dd for "' +
                                               lut_value +
                                               '" is not defined by unique value. To avoid exceptions '
                                               'procedure \n will detect the declared minimum dt "' + str(value_dt) +
                                               '" [seconds] and will set it in the model configuration file\n')

                        elif collections_dt.__len__() == 1:
                            value_dt = collections_dt[0]
                        else:
                            log_stream.error(' ===> Datasets dt is not defined')
                            raise NotImplementedError('Case not implemented yet')
                    else:
                        log_stream.error(' ===> Datasets dt is not correctly defined')
                        raise NotImplementedError('Case not implemented yet')

                    obj_dt[lut_key] = value_dt

        return obj_dt
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize namelist
    def organize_namelist(self, time_obj, template_time_ref, template_run_ref, template_run_filled):

        # Starting information
        log_stream.info(' ----> Organize namelist information ... ')

        # Define namelist filename
        filename_namelist_obj = self.set_filename_namelist(template_run_ref, template_run_filled)
        # Define namelist structure
        structure_namelist_obj = self.set_structure_namelist(
            time_obj, template_time_ref, template_run_ref, template_run_filled)

        # Starting information
        log_stream.info(' ----> Organize namelist information ... DONE')

        return filename_namelist_obj, structure_namelist_obj

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set namelist structure
    def set_structure_namelist(self, obj_time, template_time_ref, template_run_ref, template_run_filled):

        structure_namelist_filled = {}
        for template_run_key, template_run_data in template_run_filled.items():

            obj_time_step = obj_time[template_run_key]

            structure_namelist_tmp = deepcopy(self.structure_namelist_raw)
            link_namelist_raw = self.link_namelist_raw

            link_keys_none = []
            for link_root, link_obj in link_namelist_raw.items():
                for link_key, link_dict in link_obj.items():

                    if isinstance(link_dict, dict):
                        link_type = list(link_dict.keys())[0]
                        link_tags = list(link_dict.values())[0]

                        if link_type == 'algorithm':
                            obj_tmp = self.obj_algorithm
                        elif link_type == 'datasets':
                            obj_tmp = self.obj_datasets
                        elif link_type == 'time':
                            obj_tmp = obj_time_step
                        else:
                            log_stream.error(' ===> Namelist type is not correctly defined')
                            raise ValueError('Dictionary key is wrong')

                        if link_key in list(self.defined_dt.keys()):
                            value_raw = self.defined_dt[link_key]
                        else:
                            value_raw = get_dict_nested_value(obj_tmp, link_tags)

                        if value_raw is None:
                            continue
                        elif isinstance(value_raw, str):
                            template_merge_ref = {**template_run_ref, **template_time_ref}
                            value_filled = fill_tags2string(value_raw, template_merge_ref, template_run_data)
                            value_tmp = convert_template_date(value_filled)
                        else:
                            value_tmp = value_raw
                        structure_namelist_tmp[link_root][link_key] = value_tmp

                    elif link_dict is None:
                        link_keys_none.append(link_key)

            structure_namelist_filled[template_run_key] = structure_namelist_tmp

        return structure_namelist_filled
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set namelist filename
    def set_filename_namelist(self, template_ref, template_filled):
        filename_namelist_obj = {}
        for template_key, template_data in template_filled.items():
            filename_namelist_def = fill_tags2string(self.filename_namelist_raw, template_ref, template_data)
            filename_namelist_obj[template_key] = filename_namelist_def
        return filename_namelist_obj
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
