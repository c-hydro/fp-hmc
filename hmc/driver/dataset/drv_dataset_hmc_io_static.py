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

from hmc.algorithm.io.lib_data_geo_ascii import read_data_raster, read_data_grid
from hmc.algorithm.utils.lib_utils_dict import get_dict_nested_value, get_dict_value, lookup_dict_keys
from hmc.algorithm.utils.lib_utils_string import fill_tags2string

from hmc.driver.dataset.drv_dataset_hmc_io_type import DSetReader, DSetWriter, DSetComposer

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
                 dset_list_format=None, dset_list_filter=None, **kwargs):

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

                if 'hmc_file_filter' in list(dset_tmp.keys()):
                    file_filters = dset_tmp['hmc_file_filter']
                else:
                    file_filters = None

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
                        dset_obj[dset_format][var_key]['filter'] = file_filters
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
            # self.dset_static_ref = read_data_raster(file_path_ref)
            self.dset_static_ref = read_data_grid(file_path_ref, output_format='dictionary')
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
        file_filter_list = dset_source_static['file_filter'].values
        file_var_list = dset_source_static['file_var'].values

        var_frame = {}
        dset_source = None
        for var_name, file_name, file_check, file_mandatory, file_format, file_filter, file_var in zip(
                var_name_list, file_name_list, file_check_list, file_mandatory_list, file_format_list,
                file_filter_list, file_var_list):

            file_info = {'var_format': file_format, 'var_mandatory': file_mandatory,
                         'var_filter': file_filter,
                         'var_check': file_check, 'var_file': file_var}

            var_data = data_source_static[var_name]

            log_stream.info(' ------> Variable ' + var_name + ' ... ')

            if file_check or file_mandatory:

                if var_data is None:

                    if (file_name is not None) and (os.path.exists(file_name)):
                        driver_hmc_reader = DSetReader(file_name, file_info, None, time_src_info=None)
                        obj_var = driver_hmc_reader.read_filename_static(var_name)

                    elif ((file_name is not None) and (not os.path.exists(file_name))) and \
                            (var_name == 'Longitude' or var_name == 'Latitude'):

                        log_stream.warning(' ===> Static datasets for variable ' +
                                           var_name + ' not found. Datasets will be created using the terrain reference.')

                        driver_hmc_writer = DSetWriter(file_name, file_info, None, time_dst_info=None)
                        obj_var = driver_hmc_writer.write_filename_static(var_name, self.dset_static_ref)

                    elif ((file_name is not None) and (not os.path.exists(file_name))) and (var_name == 'Cell_Area'):

                        log_stream.warning(' ===> Static datasets for variable ' +
                                           var_name + ' not found. Datasets will be created using a constants method.')

                        driver_hmc_composer = DSetComposer(file_name, file_info, None, time_dst_info=None)
                        obj_var = driver_hmc_composer.compute_data_static(var_name, self.dset_static_ref)

                    else:

                        if file_mandatory:
                            log_stream.error(' ===> Static datasets for variable ' +
                                             var_name + ' in ' + file_format + ' format is mandatory. Exit.')
                            if file_name is not None:
                                raise IOError('File ' + file_name + ' not found!')
                            else:
                                raise IOError('File is declared using a None value!')
                        else:
                            log_stream.warning(' ===> Static datasets for variable ' +
                                               var_name + ' in ' + file_format + ' format is ancillary')

                            if file_format == 'shapefile':
                                log_stream.warning(
                                    ' ===> Static datasets for shapefile case will be initialized to None.')
                                obj_var = None
                            elif file_format == 'ascii_point':
                                if file_name is not None:
                                    log_stream.warning(
                                        ' ===> Static datasets for ascii point case will be initialized '
                                        'using a constants method.')
                                    driver_hmc_reader = DSetReader(file_name, file_info, None, time_src_info=None)
                                    driver_hmc_reader.write_filename_undefined(file_name, var_name)
                                else:
                                    log_stream.warning(' ===> Filename for ascii point case is declared '
                                                       'using a None value!')
                                obj_var = None
                            elif file_format == 'ascii_grid':
                                log_stream.warning(
                                    ' ===> Static datasets for ascii grid case will be initialized to None.')
                                obj_var = None
                            else:
                                log_stream.error(' ===> Static format ' + file_format + ' is not allowed. Exit.')
                                raise NotImplementedError('Case not implemented yet')

                elif var_data is not None:

                    if not os.path.exists(file_name):
                        driver_hmc_writer = DSetWriter(
                            file_name, file_info, None, time_dst_info=None,
                            file_tmp_path=None, file_tmp_clean=None)
                        obj_var = driver_hmc_writer.write_filename_static(var_name, var_data)
                    else:

                        driver_hmc_reader = DSetReader(file_name, file_info, None, time_src_info=None)
                        check_data = driver_hmc_reader.read_filename_static(var_name)

                        log_stream.info(' ------> Check variable ' + var_name + ' ... ')
                        log_stream.info(' -------> File name ' + file_name + 'for variable ' + var_name +
                                        ' is already available')

                        len_check_data = check_data.__len__()
                        len_var_data = list(var_data.keys()).__len__()
                        # for key, values in var_data.items(): # commenteted for section obj format changes
                        #    len_var_data = values.__len__()
                        #    break
                        if len_check_data == len_var_data:
                            log_stream.info(' -------> The loaded datasets and the stored datasets have the same length')
                            log_stream.info(' -------> The instance will use the stored datasets.')

                            # Merge information of the dictionaries
                            common_data = {}
                            for var_key, var_fields_step in check_data.items():
                                if var_key in list(var_data.keys()):
                                    var_fields_tmp = var_data[var_key]
                                    var_fields_common = {**var_fields_tmp, **var_fields_step}
                                    common_data[var_key] = var_fields_common
                                else:
                                    log_stream.error(' ===> Variable key ' + var_key + ' is not a common fields.')
                                    raise IOError('Obj key in merging procedures is not valid')
                            obj_var = deepcopy(common_data)
                            log_stream.info(' ------> Check variable ' + var_name + ' ... DONE')
                        else:
                            log_stream.error(' -------> The loaded datasets and the stored datasets have different lengths')
                            log_stream.error(' -------> The instance will exit for this reason.')
                            log_stream.error(' ------> Check variable ' + var_name + ' ... FAILED')
                            raise IOError('Object static length is not valid')
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
                    elif isinstance(obj_var, tuple):
                        dset_source[var_name] = obj_var
                    else:
                        log_stream.error(' ===> Data static object is not allowed')
                        raise NotImplementedError('Object static type is not valid')
                else:
                    dset_source[var_name] = obj_var

                log_stream.info(' ------> Variable ' + var_name + ' ... DONE')

            else:
                log_stream.info(' ------> Variable ' + var_name +
                                ' ... SKIPPED. File is flagged "not check" and "not mandatory".')
                if dset_source is None:
                    dset_source = {}
                dset_source[var_name] = None

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

            log_stream.info(' ------> Type ' + dset_format + ' ... ')

            dset_key_list = []
            file_path_list = []
            file_format_list = []
            file_check_list = []
            file_filter_list = []
            file_mandatory_list = []
            file_var_list = []
            for dset_key, dset_item in dset_workspace.items():

                log_stream.info(' -------> Variable ' + dset_key + ' ... ')

                folder_name_raw = dset_item[self.folder_name_tag]
                file_name_raw = dset_item[self.file_name_tag]
                file_format = dset_item['format']
                file_filter = dset_item['filter']
                file_var = dset_item['var_name']
                file_check = dset_item['var_check']
                file_mandatory = dset_item['var_mandatory']

                template_tmp = deepcopy(template_ref)
                for key in list_key_filled:
                    if key in template_tmp:
                        template_tmp.pop(key)

                template_filled_tmp = dict.fromkeys(list(template_tmp.keys()), file_var)
                template_filled_merge = {**template_filled_run, **template_filled_tmp}

                if (folder_name_raw is not None) and (file_name_raw is not None):
                    folder_name_tmp = fill_tags2string(folder_name_raw, template_ref, template_filled_merge)
                    file_name_tmp = fill_tags2string(file_name_raw, template_ref, template_filled_merge)
                    file_path_list.append(os.path.join(folder_name_tmp, file_name_tmp))
                else:
                    file_path_list.append(None)
                    log_stream.warning(' ===> Folder or/and filename is/are undefined. Initialize fields with null')

                file_format_list.append(file_format)
                file_check_list.append(file_check)
                file_filter_list.append(file_filter)
                file_mandatory_list.append(file_mandatory)
                file_var_list.append(file_var)

                dset_key_list.append(dset_key)

                log_stream.info(' -------> Variable ' + dset_key + ' ... DONE')

            df_vars = pd.DataFrame(
                {'dset_name': dset_key_list,
                 'file_name': file_path_list,
                 'file_filter': file_filter_list,
                 'file_format': file_format_list,
                 'file_check': file_check_list,
                 'file_mandatory': file_mandatory_list,
                 'file_var': file_var_list,
                 })

            df_vars = df_vars.reset_index()
            df_vars = df_vars.set_index('dset_name')

            ws_vars[dset_format] = df_vars

            log_stream.info(' ------> Type ' + dset_format + ' ... DONE')

        # Ending information
        log_stream.info(' -----> Collect static filename ... DONE')

        return ws_vars

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
