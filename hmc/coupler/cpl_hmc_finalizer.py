"""
Class Features

Name:          cpl_hmc_finalizer
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

from hmc.driver.dataset.drv_dataset_hmc_base_destination import ModelDestination

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to finalize model application
class ModelFinalizer:

    # -------------------------------------------------------------------------------------
    # Method time info
    def __init__(self, collection_dynamic, obj_geo_reference=None, obj_args=None, obj_run=None, obj_ancillary=None):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.collection_dynamic = collection_dynamic
        self.obj_geo_reference = obj_geo_reference
        self.obj_args = obj_args
        self.obj_run = obj_run
        self.obj_ancillary = obj_ancillary

        self.driver_io_destination = ModelDestination(
            collection_dynamic=self.collection_dynamic,
            obj_dataset=self.obj_args.obj_datasets,
            obj_geo_reference=self.obj_geo_reference,
            template_time=self.obj_args.obj_template_time_ref,
            template_run_def=self.obj_run.obj_template_run_filled,
            template_run_ref=self.obj_args.obj_template_run_ref,
            template_static=self.obj_args.obj_template_dset_static_ref,
            template_outcome=self.obj_args.obj_template_dset_outcome_ref)

        self.flag_cleaning_dynamic_outcome = self.obj_args.obj_datasets['Flags'][
            'cleaning_ancillary_data_dynamic_outcome']

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to configure outcome datasets
    def configure_dynamic_datasets(self, time_series_collections, time_info_collections,
                                   static_datasets_collections, ancillary_datasets_collections,
                                   ancillary_tag_type='dynamic_outcome'):

        # Starting info
        log_stream.info(' #### Configure dynamic outcome datasets ... ')

        file_path_ancillary = ancillary_datasets_collections[ancillary_tag_type]
        if self.flag_cleaning_dynamic_outcome:
            if os.path.exists(file_path_ancillary):
                os.remove(file_path_ancillary)

        if not os.path.exists(file_path_ancillary):

            # Get template variable(s)
            template_run_filled = self.obj_run.obj_template_run_filled

            # Method to organize outcome datasets
            outcome_datasets_obj = self.driver_io_destination.organize_data_dynamic(
                time_series_collections, static_datasets_collections, template_run_filled,
                tag_exectype='SIM', tag_datadriver='outcome')

            # Method to analyze outcome datasets
            self.driver_io_destination.analyze_data_dynamic(
                time_series_collections, time_info_collections, static_datasets_collections, outcome_datasets_obj,
                tag_exectype='SIM', tag_datatype='ARCHIVE', tag_datadriver='outcome')

            # Method to organize state datasets
            state_datasets_obj = self.driver_io_destination.organize_data_dynamic(
                time_series_collections, static_datasets_collections, template_run_filled,
                tag_exectype='SIM', tag_datadriver='state')

            # Method to analyze state datasets
            self.driver_io_destination.analyze_data_dynamic(
                time_series_collections, time_info_collections, static_datasets_collections, state_datasets_obj,
                tag_exectype='SIM', tag_datatype='ARCHIVE', tag_datadriver='state')

            # Retrieve dynamic collections
            dynamic_datasets_collections = self.driver_io_destination.dset_collections_dynamic

            # Method to write static datasets collections
            write_workspace_obj(file_path_ancillary, dynamic_datasets_collections)

            # Ending info
            log_stream.info(' #### Configure dynamic outcome datasets ... DONE')

        elif os.path.exists(file_path_ancillary):

            # Method to read static datasets collections
            dynamic_datasets_collections = read_workspace_obj(file_path_ancillary)

            # Ending info
            log_stream.info(' #### Configure dynamic outcome datasets ... LOADED. Restore file: ' + file_path_ancillary)

        else:
            # Error in ancillary file
            log_stream.info(' #### Configure dynamic outcome datasets ... FAILED')
            log_stream.error(' ===> Ancillary file for dynamic outcome datasets collections is not correctly defined')
            raise RuntimeError('Bad definition of ancillary dynamic file')

        return dynamic_datasets_collections

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to configure summary datasets
    def configure_summary_datasets(self, time_series_collections, time_info_collections,
                                   static_datasets_collections, outcome_datasets_collections):

        # Starting info
        log_stream.info(' #### Configure summary outcome datasets ... ')

        # Get template variable(s)
        template_run_filled = self.obj_run.obj_template_run_filled

        # Method to organize summary datasets
        summary_datasets_obj = self.driver_io_destination.organize_data_summary(
            time_series_collections, static_datasets_collections, template_run_filled,
            tag_exectype='POST_PROCESSING', tag_datadriver='summary')

        # Method to analyze summary datasets
        self.driver_io_destination.analyze_data_summary(
            outcome_datasets_collections,
            time_series_collections, time_info_collections, static_datasets_collections, summary_datasets_obj,
            template_run_filled,
            tag_exectype='POST_PROCESSING', tag_datadriver='summary')

        # Ending info
        log_stream.info(' #### Configure summary outcome datasets ... DONE')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
