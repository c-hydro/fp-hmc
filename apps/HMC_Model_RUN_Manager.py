#!/usr/bin/python3
"""
HYDROLOGICAL MODEL CONTINUUM - Run manager to set parameters and datasets of the hydrological model

__date__ = '20201102'
__version__ = '3.1.3'
__author__ =
        'Fabio Delogu (fabio.delogu@cimafoundation.org',
        'Simone Gabellani (simone.gabellani@cimafoundation.org',
        'Francesco Silvestro (francesco.silvestro@cimafoundation.org'

__library__ = 'hmc'

General command line:
    python3 HMC_Model_RUN_Manager.py
        -settings_algorithm configuration_algorithm.json.json
        -settings_data configuration_datasets.json
        -time "YYYY-MM-DD HH:MM"

Parameters:
    -settings_algorithm : string
        Name of the settings algorithm file in json format
    -settings_datasets : string
        Name of the settings datasets file in json format
    -time: string
        Time of the simulation in YYYY-MM-DD HH:MM format

Version(s):
20201102 (3.1.3) --> Development of run manager application for version 3.1.3 of HMC models
20200723 (3.1.2) --> Development of run manager application for version 3.1.2 of HMC models
20200401 (3.0.0) --> Beta release of run manager application for 3th generation of HMC models
"""

# -------------------------------------------------------------------------------------
# Libraries
import argparse
import time

# Import coupler and driver classes
from hmc.driver.configuration.drv_configuration_hmc_logging import ModelLogging
from hmc.coupler.cpl_hmc_manager import ModelInitializer, ModelCleaner
from hmc.coupler.cpl_hmc_builder import ModelBuilder
from hmc.coupler.cpl_hmc_runner import ModelRunner
from hmc.coupler.cpl_hmc_finalizer import ModelFinalizer
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get script argument(s)
def get_args(settings_algorithm=None, settings_datasets=None, settings_time=None):

    parser_handle = argparse.ArgumentParser()
    parser_handle.add_argument('-settings_algorithm', action="store", dest="settings_algorithm")
    parser_handle.add_argument('-settings_datasets', action="store", dest="settings_datasets")
    parser_handle.add_argument('-time', action="store", dest="time")
    parser_values = parser_handle.parse_args()

    script_name = parser_handle.prog

    if settings_algorithm is None:
        if parser_values.settings_algorithm:
            script_settings_algorithm = parser_values.settings_algorithm
        else:
            script_settings_algorithm = 'configuration_algorithm.json'
    else:
        script_settings_algorithm = settings_algorithm

    if settings_datasets is None:
        if parser_values.settings_datasets:
            script_settings_datasets = parser_values.settings_datasets
        else:
            script_settings_datasets = 'configuration_datasets.json'
    else:
        script_settings_datasets = settings_datasets

    if settings_time is None:
        if parser_values.time:
            script_time = parser_values.time
        else:
            script_time = None
    else:
        script_time = settings_time

    return script_name, script_settings_algorithm, script_settings_datasets, script_time

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Script Main
def main(settings_algorithm=None, settings_datasets=None, settings_time=None):

    # -------------------------------------------------------------------------------------
    # Version and algorithm information
    project_name = 'HMC'
    alg_version = '3.1.3'
    alg_type = 'Model'
    alg_name = 'RUN MANAGER TOOL'
    # Time algorithm information
    time_start = time.time()

    # Get script argument(s)
    script_name, script_settings_algorithm, \
    script_settings_datasets, script_time = get_args(settings_algorithm, settings_datasets, settings_time)

    # Set logging file
    driver_hmc_logging = ModelLogging(script_settings_algorithm)
    log_stream = driver_hmc_logging.configure_logging()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Start Program
    log_stream.info('[' + project_name + ' ' + alg_type + ' - ' + alg_name + ' (Version ' + alg_version + ')]')
    log_stream.info('[' + project_name + '] Start Program ... ')
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Configure model initializer class
    driver_hmc_initializer = ModelInitializer(file_algorithm=script_settings_algorithm,
                                              file_datasets=script_settings_datasets, time=script_time)

    # Configure algorithm
    time_series_collections, time_info_collections, \
        run_info_collections, run_cline_collections = driver_hmc_initializer.configure_algorithm()

    # Configure ancillary datasets
    ancillary_datasets_collections = driver_hmc_initializer.configure_ancillary_datasets(time_info_collections)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Configure model builder class
    driver_hmc_builder = ModelBuilder(
        obj_geo_reference=driver_hmc_initializer.dset_ref_geo,
        obj_args=driver_hmc_initializer.obj_args,
        obj_run=driver_hmc_initializer.obj_run,
        obj_ancillary=driver_hmc_initializer.obj_ancillary)

    # Configure static datasets
    static_datasets_collections = driver_hmc_builder.configure_static_datasets(ancillary_datasets_collections)
    # Configure dynamic datasets
    forcing_datasets_collections = driver_hmc_builder.configure_dynamic_datasets(
        time_series_collections, time_info_collections, static_datasets_collections, ancillary_datasets_collections)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Configure model runner class
    driver_hmc_runner = ModelRunner(time_info=time_info_collections, run_info=run_info_collections,
                                    command_line_info=run_cline_collections,
                                    obj_args=driver_hmc_initializer.obj_args,
                                    obj_ancillary=driver_hmc_initializer.obj_ancillary)
    # Configure model execution
    driver_hmc_runner.configure_execution(ancillary_datasets_collections)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Configure model finalizer class
    driver_hmc_finalizer = ModelFinalizer(
        collection_dynamic=forcing_datasets_collections,
        obj_geo_reference=driver_hmc_initializer.dset_ref_geo,
        obj_args=driver_hmc_initializer.obj_args,
        obj_run=driver_hmc_initializer.obj_run,
        obj_ancillary=driver_hmc_initializer.obj_ancillary)

    # Configure outcome datasets
    outcome_datasets_collections = driver_hmc_finalizer.configure_dynamic_datasets(
        time_series_collections, time_info_collections, static_datasets_collections, ancillary_datasets_collections)
    # Configure summary datasets
    driver_hmc_finalizer.configure_summary_datasets(
        time_series_collections, time_info_collections, static_datasets_collections, outcome_datasets_collections)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Configure model cleaner class
    driver_hmc_cleaner = ModelCleaner(
        collections_ancillary=ancillary_datasets_collections,
        obj_args=driver_hmc_initializer.obj_args,
        obj_run=driver_hmc_initializer.obj_run,
    )
    # Configure cleaning tmp datasets
    driver_hmc_cleaner.configure_cleaner()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Note about script parameter(s)
    log_stream.info('NOTE - Algorithm parameter(s)')
    log_stream.info('Script: ' + str(script_name))
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # End Program
    time_elapsed = round(time.time() - time_start, 1)

    log_stream.info('[' + project_name + ' ' + alg_type + ' - ' + alg_name + ' (Version ' + alg_version + ')]')
    log_stream.info('End Program - Time elapsed: ' + str(time_elapsed) + ' seconds')
    # -------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------
