"""
Class Features

Name:          cpl_hmc_builder
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os

from hmc.algorithm.default.lib_default_args import logger_name
from hmc.algorithm.debug.lib_debug import read_workspace_obj, write_workspace_obj

from hmc.driver.dataset.drv_dataset_hmc_base_source import ModelSource

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to built model application
class ModelBuilder:

    # -------------------------------------------------------------------------------------
    # Method time info
    def __init__(self, obj_geo_reference=None, obj_args=None, obj_run=None, obj_ancillary=None):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.obj_geo_reference = obj_geo_reference
        self.obj_args = obj_args
        self.obj_run = obj_run
        self.obj_ancillary = obj_ancillary

        self.driver_io_source = ModelSource(
            self.obj_args.obj_datasets,
            template_time=self.obj_args.obj_template_time_ref,
            template_run_def=self.obj_run.obj_template_run_filled,
            template_run_ref=self.obj_args.obj_template_run_ref,
            template_static=self.obj_args.obj_template_dset_static_ref,
            template_dynamic=self.obj_args.obj_template_dset_dynamic_ref)

        self.flag_cleaning_static = self.obj_args.obj_datasets['Flags']['cleaning_ancillary_data_static']
        self.flag_cleaning_dynamic_source = self.obj_args.obj_datasets['Flags']['cleaning_ancillary_data_dynamic_source']

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to configure static datasets
    def configure_static_datasets(self, ancillary_datasets_collections, ancillary_tag_type='static'):

        # Starting info
        log_stream.info(' #### Configure static datasets ... ')

        file_path_ancillary = ancillary_datasets_collections[ancillary_tag_type]
        if self.flag_cleaning_static:
            if os.path.exists(file_path_ancillary):
                os.remove(file_path_ancillary)

        if not os.path.exists(file_path_ancillary):

            # Get template variable(s)
            template_run = self.obj_run.obj_template_run_filled
            # Get the template using the first run (deterministic or probabilistic)
            template_def = list(template_run.values())[0]

            # Method to organize static datasets
            static_datasets_obj = self.driver_io_source.organize_data_static(template_def)

            # Method to analyze and collect static datasets
            static_datasets_collections = self.driver_io_source.analyze_data_static(static_datasets_obj)

            # Method to write static datasets collections
            write_workspace_obj(file_path_ancillary, static_datasets_collections)

            # Ending info
            log_stream.info(' #### Configure static datasets ... DONE')

        elif os.path.exists(file_path_ancillary):

            # Method to read static datasets collections
            static_datasets_collections = read_workspace_obj(file_path_ancillary)

            # Ending info
            log_stream.info(' #### Configure static datasets ... LOADED. Restore file: ' + file_path_ancillary)

        else:

            log_stream.error(' ===> Ancillary file for static datasets collections is not correctly defined')
            raise RuntimeError('Bad definition of ancillary static file')

        return static_datasets_collections
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to configure dynamic datasets
    def configure_dynamic_datasets(self, time_series_collections, time_info_collections,
                                   static_datasets_collections, ancillary_datasets_collections,
                                   ancillary_tag_type='dynamic_source'):

        # Starting info
        log_stream.info(' #### Configure dynamic source datasets ... ')

        file_path_ancillary = ancillary_datasets_collections[ancillary_tag_type]
        if self.flag_cleaning_dynamic_source:
            if os.path.exists(file_path_ancillary):
                os.remove(file_path_ancillary)

        if not os.path.exists(file_path_ancillary):

            # Get template variable(s)
            template_run_filled = self.obj_run.obj_template_run_filled

            # Method to organize dynamic restart datasets
            restart_datasets_obj = self.driver_io_source.organize_data_dynamic(
                time_series_collections, template_run_filled,
                static_datasets_collections=None, tag_datadriver='restart')

            # Method to organize dynamic forcing datasets
            dynamic_datasets_obj = self.driver_io_source.organize_data_dynamic(
                time_series_collections, template_run_filled,
                static_datasets_collections=static_datasets_collections, tag_datadriver='forcing')

            # Method to analyze dynamic restart datasets
            self.driver_io_source.analyze_data_dynamic_restart(
                time_series_collections, time_info_collections, static_datasets_collections, restart_datasets_obj,
                tag_datatype='ARCHIVE', tag_datadriver='restart')

            # Method to analyze dynamic forcing datasets
            self.driver_io_source.analyze_data_dynamic_forcing(
                time_series_collections, time_info_collections, static_datasets_collections, dynamic_datasets_obj,
                tag_datatype='OBS', tag_datadriver='forcing')
            self.driver_io_source.analyze_data_dynamic_forcing(
                time_series_collections, time_info_collections, static_datasets_collections, dynamic_datasets_obj,
                tag_datatype='FOR', tag_datadriver='forcing')

            # Retrieve dynamic collections
            dynamic_datasets_collections = self.driver_io_source.dset_collections_dynamic

            # Method to write static datasets collections
            write_workspace_obj(file_path_ancillary, dynamic_datasets_collections)

            # Ending info
            log_stream.info(' #### Configure dynamic source datasets ... DONE')

        elif os.path.exists(file_path_ancillary):

            # Method to read static datasets collections
            dynamic_datasets_collections = read_workspace_obj(file_path_ancillary)

            # Ending info
            log_stream.info(' #### Configure dynamic source datasets ... LOADED. Restore file:' + file_path_ancillary)

        else:
            # Error in ancillary file
            log_stream.info(' #### Configure dynamic source datasets ... FAILED')
            log_stream.error(' ===> Ancillary file for dynamic source datasets collections is not correctly defined')
            raise RuntimeError('Bad definition of ancillary dynamic file')

        return dynamic_datasets_collections

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
