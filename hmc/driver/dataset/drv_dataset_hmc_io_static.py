"""
Class Features

Name:          drv_dataset_hmc_io_static
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os

import xarray as xr
import pandas as pd

from copy import deepcopy

from hmc.algorithm.utils.lib_utils_geo import get_raster
from hmc.algorithm.utils.lib_utils_dict import get_dict_nested_value, get_dict_value, lookup_dict_keys
from hmc.algorithm.utils.lib_utils_string import fill_tags2string

from hmc.driver.dataset.drv_dataset_hmc_io_type import DSetReader, DSetWriter

from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to read datasets
class DSetManager:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, dset, template_static_ref=None, template_run_ref=None, template_run_def=None,
                 model_tag='hmc', datasets_tag='datasets',
                 dset_list_format=None, **kwargs):

        if dset_list_format is None:
            dset_list_format = ['Shapefile', 'Point', 'Gridded']

        self.dset = dset
        self.dset_list_format = dset_list_format

        self.template_static_ref = template_static_ref
        self.template_run_ref = template_run_ref
        self.template_run_def = list(template_run_def.values())[0]

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.dset_ref_tag = ['Gridded', 'Terrain']

        self.model_tag = model_tag
        self.datasets_tag = datasets_tag

        dset_obj = {}
        for dset_format in dset_list_format:

            if dset_format in self.dset:
                dset_obj[dset_format] = {}

                dset_tmp = self.dset[dset_format]

                file_name = dset_tmp['hmc_file_name']
                file_folder = dset_tmp['hmc_file_folder']
                file_format = dset_tmp['hmc_file_format']
                file_frequency = dset_tmp['hmc_file_frequency']
                file_vars = dset_tmp['hmc_file_variable']

                if file_vars.__len__() > 0:

                    for var_key, var_data in file_vars.items():

                        dset_obj[dset_format][var_key] = {}

                        var_name = var_data['var_name']
                        var_check = var_data['check']
                        var_mandatory = var_data['mandatory']

                        dset_obj[dset_format][var_key][self.file_name_tag] = file_name
                        dset_obj[dset_format][var_key][self.folder_name_tag] = file_folder
                        dset_obj[dset_format][var_key]['format'] = file_format
                        dset_obj[dset_format][var_key]['frequency'] = file_frequency
                        dset_obj[dset_format][var_key]['var_name'] = var_name
                        dset_obj[dset_format][var_key]['var_check'] = var_check
                        dset_obj[dset_format][var_key]['var_mandatory'] = var_mandatory

                else:
                    dset_obj[dset_format] = None

        self.dset_obj = dset_obj

        self.dset_ref_obj = get_dict_nested_value(self.dset_obj, self.dset_ref_tag)

        template_static_def = dict.fromkeys(list(self.template_static_ref.keys()), self.dset_ref_obj['var_name'])

        template_ref_merge = {**self.template_run_ref, **template_static_ref}
        template_def_merge = {**self.template_run_def, **template_static_def}

        folder_name_ref = fill_tags2string(self.dset_ref_obj[self.folder_name_tag],
                                           template_ref_merge, template_def_merge)
        file_name_ref = fill_tags2string(self.dset_ref_obj[self.file_name_tag], template_ref_merge, template_def_merge)

        file_path_ref = os.path.join(folder_name_ref, file_name_ref)

        if os.path.exists(file_path_ref):
            self.dset_static_ref = get_raster(file_path_ref)
        else:
            log_stream.error(' ===> Reference static datasets is not available')
            raise IOError('File is not found in the selected folder')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect datasets
    def collect_data(self, dset_source_static, data_source_static=None):

        # Starting information
        log_stream.info(' -----> Collect static datasets ... ')

        var_name_list = list(dset_source_static.index)
        file_name_list = dset_source_static['file_name'].values
        file_check_list = dset_source_static['file_check'].values
        file_mandatory_list = dset_source_static['file_mandatory'].values
        file_format_list = dset_source_static['file_format'].values

        var_frame = {}
        dset_source = None
        for var_name, file_name, file_check, file_mandatory, file_format in zip(
                var_name_list, file_name_list, file_check_list, file_mandatory_list, file_format_list):

            file_info = {'var_format': file_format, 'var_mandatory': file_mandatory, 'var_check': file_check}

            var_data = data_source_static[var_name]

            if var_data is None:
                driver_hmc_parser = DSetReader(file_name, file_info, None, time_src_info=None)
                obj_var = driver_hmc_parser.read_filename_static(var_name)
            elif var_data is not None:
                driver_hmc_parser = DSetWriter(file_name, file_info, None, time_dst_info=None)
                obj_var = driver_hmc_parser.write_filename_static(var_name, var_data)
            else:
                log_stream.error(' ===> Variable data format is not allowed')
                raise NotImplementedError('Object static format is not valid')

            if dset_source is None:
                dset_source = {}

            if obj_var is not None:

                if isinstance(obj_var, xr.DataArray):
                    dset_source[var_name] = obj_var
                elif isinstance(obj_var, dict):
                    dset_source[var_name] = obj_var
                elif isinstance(obj_var, list):
                    dset_source[var_name] = obj_var
                else:
                    log_stream.error(' ===> Data static object is not allowed')
                    raise NotImplementedError('Object static type is not valid')
            else:
                dset_source[var_name] = obj_var

        var_frame[self.datasets_tag] = dset_source

        # Ending information
        log_stream.info(' -----> Collect static datasets ... DONE')

        return var_frame

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect filename
    def collect_filename(self, template_ref, template_filled_run):

        # Starting information
        log_stream.info(' -----> Collect static filename ... ')

        dset_obj = self.dset_obj
        list_key_filled = list(template_filled_run.keys())

        ws_vars = {}
        for dset_format, dset_workspace in dset_obj.items():

            dset_key_list = []
            file_path_list = []
            file_format_list = []
            file_check_list = []
            file_mandatory_list = []
            for dset_key, dset_item in dset_workspace.items():

                folder_name_raw = dset_item[self.folder_name_tag]
                file_name_raw = dset_item[self.file_name_tag]
                file_format = dset_item['format']
                file_var = dset_item['var_name']
                file_check = dset_item['var_check']
                file_mandatory = dset_item['var_mandatory']

                template_tmp = deepcopy(template_ref)
                for key in list_key_filled:
                    if key in template_tmp:
                        template_tmp.pop(key)

                template_filled_tmp = dict.fromkeys(list(template_tmp.keys()), file_var)
                template_filled_merge = {**template_filled_run, **template_filled_tmp}

                folder_name_tmp = fill_tags2string(folder_name_raw, template_ref, template_filled_merge)
                file_name_tmp = fill_tags2string(file_name_raw, template_ref, template_filled_merge)

                file_path_list.append(os.path.join(folder_name_tmp, file_name_tmp))
                file_format_list.append(file_format)
                file_check_list.append(file_check)
                file_mandatory_list.append(file_mandatory)

                dset_key_list.append(dset_key)

            df_vars = pd.DataFrame(
                {'dset_name': dset_key_list,
                 'file_name': file_path_list,
                 'file_format': file_format_list,
                 'file_check': file_check_list,
                 'file_mandatory': file_mandatory_list,
                 })

            df_vars = df_vars.reset_index()
            df_vars = df_vars.set_index('dset_name')

            ws_vars[dset_format] = df_vars

        # Ending information
        log_stream.info(' -----> Collect static filename ... DONE')

        return ws_vars

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
