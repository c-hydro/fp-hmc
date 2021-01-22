"""
Class Features

Name:          cpl_hmc_manager
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os

from hmc.algorithm.utils.lib_utils_geo import get_raster
from hmc.algorithm.utils.lib_utils_dict import get_dict_nested_value, get_dict_value
from hmc.algorithm.utils.lib_utils_string import fill_tags2string
from hmc.algorithm.utils.lib_utils_system import delete_folder

from hmc.algorithm.default.lib_default_args import logger_name

from hmc.driver.configuration.drv_configuration_hmc_args import ModelArgs
from hmc.driver.configuration.drv_configuration_hmc_time import ModelTime
from hmc.driver.configuration.drv_configuration_hmc_run import ModelRun
from hmc.driver.configuration.drv_configuration_hmc_namelist import ModelNamelist

from hmc.driver.dataset.drv_dataset_hmc_base_ancillary import ModelAncillary

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to init model application
class ModelInitializer:

    # -------------------------------------------------------------------------------------
    # Method time info
    def __init__(self, file_algorithm=None, file_datasets=None, time=None):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.file_algorithm = file_algorithm
        self.file_datasets = file_datasets
        self.time = time

        self.obj_args = ModelArgs(self.file_algorithm, self.file_datasets, self.time)

        self.obj_time = ModelTime(self.obj_args.obj_time_arg, self.obj_args.obj_time_info_ref,
                                  template_time=self.obj_args.obj_template_time_ref)

        self.obj_namelist = ModelNamelist(self.obj_args.obj_algorithm, self.obj_args.obj_datasets)

        self.obj_run = ModelRun(self.obj_args.obj_run_info_ref, template_run=self.obj_args.obj_template_run_ref)

        self.obj_ancillary = ModelAncillary(self.obj_args.obj_datasets,
                                            template_time=self.obj_args.obj_template_time_ref,
                                            template_run_def=self.obj_run.obj_template_run_filled,
                                            template_run_ref=self.obj_args.obj_template_run_ref,
                                            template_static=self.obj_args.obj_template_dset_static_ref,
                                            template_dynamic=self.obj_args.obj_template_dset_dynamic_ref)

        self.flag_cleaning_static = self.obj_args.obj_datasets['Flags']['cleaning_ancillary_data_static']
        self.flag_cleaning_dynamic_source = self.obj_args.obj_datasets['Flags'][
            'cleaning_ancillary_data_dynamic_source']
        self.flag_cleaning_dynamic_outcome = self.obj_args.obj_datasets['Flags'][
            'cleaning_ancillary_data_dynamic_outcome']
        self.flag_cleaning_dynamic_exec = self.obj_args.obj_datasets['Flags'][
            'cleaning_ancillary_data_dynamic_execution']

        self.dset_ref_tag = ['DataGeo', 'Gridded']
        self.dset_ref_variable = 'Terrain'

        self.dset_ref_geo = self.set_reference_raster()
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set the reference raster
    def set_reference_raster(self):

        template_run_def = list(self.obj_run.obj_template_run_filled.values())[0]
        dset_obj_tmp = get_dict_nested_value(self.obj_args.obj_datasets, self.dset_ref_tag)

        file_name_raw = dset_obj_tmp['hmc_file_name']
        folder_name_raw = dset_obj_tmp['hmc_file_folder']

        file_variable_ref = dset_obj_tmp['hmc_file_variable'][self.dset_ref_variable]

        template_static_def = dict.fromkeys(list(self.obj_args.obj_template_dset_static_ref.keys()), file_variable_ref['var_name'])

        template_ref_merge = {**self.obj_args.obj_template_run_ref, **self.obj_args.obj_template_dset_static_ref}
        template_def_merge = {**template_run_def, **template_static_def}

        folder_name_ref = fill_tags2string(folder_name_raw, template_ref_merge, template_def_merge)
        file_name_ref = fill_tags2string(file_name_raw, template_ref_merge, template_def_merge)
        file_path_ref = os.path.join(folder_name_ref, file_name_ref)

        if os.path.exists(file_path_ref):
            dset_ref = get_raster(file_path_ref)
        else:
            log_stream.error(' ===> Reference static datasets is not available')
            raise IOError('File is not found in the selected folder')
        return dset_ref
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to configure algorithm
    def configure_algorithm(self):

        # Starting info
        log_stream.info(' #### Configure algorithm ... ')

        # Get template variable(s)
        template_time_ref = self.obj_args.obj_template_time_ref
        template_run_ref = self.obj_args.obj_template_run_ref
        template_run_filled = self.obj_run.obj_template_run_filled

        # Method to organize time dataframe and series dictionary
        time_info_obj, time_series_obj = self.obj_time.organize_time(
            self.obj_run.obj_run_info_filled, self.dset_ref_geo)

        # Method to organize namelist dataframe
        namelist_filename_obj, namelist_structure_obj = self.obj_namelist.organize_namelist(
            time_info_obj, template_time_ref, template_run_ref, template_run_filled)

        # Method to organize run execution
        run_cline_obj = self.obj_run.organize_run_execution(namelist_filename_obj, namelist_structure_obj)
        # Method to organize run information
        run_info_obj = self.obj_run.organize_run_dependencies()

        # Ending info
        log_stream.info(' #### Configure algorithm ... DONE')

        return time_series_obj, time_info_obj, run_info_obj, run_cline_obj

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to configure ancillary datasets
    def configure_ancillary_datasets(self, time_info_collections):

        # Starting info
        log_stream.info(' #### Configure ancillary datasets ... ')

        ancillary_datasets_collections = self.obj_ancillary.organize_data_ancillary(time_info_collections)

        # Ending info
        log_stream.info(' #### Configure ancillary datasets ... DONE')

        return ancillary_datasets_collections

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Class to clean model application
class ModelCleaner:

    # -------------------------------------------------------------------------------------
    # Method time info
    def __init__(self, collections_ancillary=None, obj_args=None, obj_run=None):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.collections_ancillary = collections_ancillary
        self.obj_args = obj_args
        self.obj_run = obj_run

        self.tag_run_logging = 'log'
        self.tag_run_root_generic = 'run_root_generic'
        self.tag_run_root_main = 'run_root_main'
        self.tag_run_flag_run_execution = 'cleaning_run_execution'
        self.tag_run_flag_run_logging = 'cleaning_run_logging'
        self.tag_run_tmp = 'cleaning_run_tmp'

        self.folder_run_root_generic = self.set_tag_value(self.obj_run.obj_run_path, self.tag_run_root_generic)
        self.folder_run_root_main = self.set_tag_value(self.obj_run.obj_run_path, self.tag_run_root_main)

        self.file_path_logging = self.set_tag_value(self.obj_run.obj_run_path, self.tag_run_logging)

        self.cleaning_flag_run_tmp = self.set_tag_value(self.obj_args.obj_datasets, self.tag_run_tmp)
        self.cleaning_flag_run_execution = self.set_tag_value(self.obj_args.obj_datasets,
                                                              self.tag_run_flag_run_execution)
        self.cleaning_flag_run_logging = self.set_tag_value(self.obj_args.obj_datasets,
                                                            self.tag_run_flag_run_logging)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set value of the tags
    @staticmethod
    def set_tag_value(obj_data, tag_data):
        items_raw = get_dict_value(obj_data, tag_data, [])
        if items_raw.__len__() == 0:
            items_raw = [None]
        items_unique = list(set(items_raw))
        if items_unique.__len__() != 1:
            log_stream.warning(' ===> Tag definition is greater then one item. Could be error in cleaning tmp datasets')
        return items_unique[0]
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean tmp datasets
    def configure_cleaner(self):

        # Starting info
        log_stream.info(' #### Configure cleaning datasets ... ')

        # Method to clean ancillary archive
        self.clean_run_tmp(self.cleaning_flag_run_tmp)

        # Method to clean run execution
        self.clean_run_execution(self.cleaning_flag_run_execution)

        # Method to clean run logging
        self.clean_run_logging(self.cleaning_flag_run_logging)

        # Ending info
        log_stream.info(' #### Configure cleaning datasets ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean ancillary archive
    def clean_run_tmp(self, flag_run_tmp):

        log_stream.info(' ----> Clean run temporary datasets ... ')

        collection_ancillary = self.collections_ancillary

        if flag_run_tmp:

            collection_path_tmp = []
            for collection_key, collection_filepath in collection_ancillary.items():
                if os.path.exists(collection_filepath):
                    collection_path_root = os.path.split(collection_filepath)[0]
                    collection_path_tmp.append(collection_path_root)
                    os.remove(collection_filepath)

            collection_path_tmp = list(set(collection_path_tmp))
            for collection_path_step in collection_path_tmp:
                if not os.listdir(collection_path_step):
                    delete_folder(collection_path_step)
                else:
                    log_stream.warning(' ===> Folder: ' + collection_path_step + ' is not empty')
            log_stream.info(' ----> Clean run temporary datasets ... DONE')
        else:
            log_stream.info(' ----> Clean run temporary datasets ... SKIPPED. Flag is not activated')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean run logging
    def clean_run_logging(self, flag_run_logging):

        log_stream.info(' ----> Clean run logging ... ')
        file_path_logging = self.file_path_logging
        if flag_run_logging:
            folder_name_logging, file_name_logging = os.path.split(file_path_logging)

            if os.path.exists(file_path_logging):
                os.remove(file_path_logging)

            if not os.listdir(folder_name_logging):
                delete_folder(folder_name_logging)
            else:
                log_stream.warning(' ===> Folder: ' + folder_name_logging + ' is not empty')

            log_stream.info(' ----> Clean run logging ... DONE')
        else:
            log_stream.info(' ----> Clean run logging ... SKIPPED. Flag is not activated')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean run execution
    def clean_run_execution(self, flag_run_execution):

        log_stream.info(' ----> Clean run execution ... ')

        folder_run_root_generic = self.folder_run_root_generic

        if flag_run_execution:

            collection_path_tmp = []
            for folder_name_step, _, file_name_list in os.walk(folder_run_root_generic):
                for file_name_step in file_name_list:
                    file_path_step = os.path.join(folder_name_step, file_name_step)
                    if os.path.isfile(file_path_step):
                        if os.path.exists(file_path_step):
                            os.remove(file_path_step)
                        else:
                            log_stream.warning(' ===> Filename: ' + file_path_step + ' does not exist')
                    elif os.path.isdir(file_path_step):
                        collection_path_tmp.append(file_path_step)
                    else:
                        log_stream.warning(' ===> Item ' + file_path_step + ' is not recognized as known support')

                if not os.listdir(folder_name_step):
                    delete_folder(folder_name_step)
                else:
                    collection_path_tmp.append(folder_name_step)

            for folder_name_step, _, _ in os.walk(folder_run_root_generic, topdown=False):

                if folder_name_step == folder_run_root_generic:
                    break
                if os.path.isdir(folder_name_step):
                    if not os.listdir(folder_name_step):
                        delete_folder(folder_name_step)
                    else:
                        log_stream.warning(' ===> Folder: ' + folder_name_step + ' is not empty')

            log_stream.info(' ----> Clean run execution ... DONE')
        else:
            log_stream.info(' ----> Clean run execution ... SKIPPED. Flag is not activated')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
