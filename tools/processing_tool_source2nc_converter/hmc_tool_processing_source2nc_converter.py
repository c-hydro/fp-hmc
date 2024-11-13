#!/usr/bin/python3

"""
HYDROLOGICAL MODEL CONTINUUM - Tool source2nc converter
__date__ = '20241113'
__version__ = '1.3.0'
__author__ =
        'Lorenzo Alfieri' (lorenzo.alfieri@cimafoundation.org',
        'Andrea Libertino (andrea.libertino@cimafoundation.org',
        'Fabio Delogu' (fabio.delogu@cimafoundation.org',

__library__ = 'hmc'

General command line:
python hmc_tool_processing_src2nc_converter.py -settings_file "configuration.json" -time "YYYY-MM-DD HH:MM"

Version(s):
20241113 (1.3.0) --> Add/manage the options to not declare the source grid/file information in the configuration file
20211126 (1.2.0) --> Add the operational mode and the s3m datasets format to the sources
20211012 (1.1.0) --> Add the restart datasets in binary format to the sources
20210408 (1.0.0) --> Refactor to manage different format for source datasets
20201214 (0.0.2) --> Various bug fixes
20201203 (0.0.1) --> Beta release
"""
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Library
import logging
import os
import argparse
import time

from tools.processing_tool_source2nc_converter.lib_utils_logging import set_logging_file
from tools.processing_tool_source2nc_converter.lib_utils_time import set_time
from tools.processing_tool_source2nc_converter.lib_data_io_json import read_file_settings
from tools.processing_tool_source2nc_converter.lib_info_args import logger_name, time_format_algorithm

from tools.processing_tool_source2nc_converter.driver_data_io_static import DriverStatic
from tools.processing_tool_source2nc_converter.driver_data_io_dynamic import DriverDynamic

# Logging
log_stream = logging.getLogger(logger_name)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Algorithm information
project_name = 'HMC'
alg_name = 'TOOL SOURCE2NC CONVERTER'
alg_type = 'Model'
alg_version = '1.3.0'
alg_release = '2024-11-13'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Script Main
def main():

    # -------------------------------------------------------------------------------------
    # Get algorithm settings
    alg_settings, alg_time = get_args()

    # Set algorithm settings
    data_settings = read_file_settings(alg_settings)

    # Set algorithm logging
    set_logging_file(
        logger_name=logger_name,
        logger_file=os.path.join(data_settings['log']['folder_name'], data_settings['log']['file_name']))
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    log_stream.info(' ============================================================================ ')
    log_stream.info('[' + project_name + ' ' + alg_type + ' - ' + alg_name + ' (Version ' + alg_version +
                    ' - Release ' + alg_release + ')]')
    log_stream.info(' ==> START ... ')
    log_stream.info(' ')

    # Time algorithm information
    alg_time_start = time.time()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Organize time run
    time_run, time_range, time_chunks = set_time(
        time_run_args=alg_time,
        time_run_file=data_settings['time']['time_run'],
        time_run_file_start=data_settings['time']['time_start'],
        time_run_file_end=data_settings['time']['time_end'],
        time_format=time_format_algorithm,
        time_period=data_settings['time']['time_period'],
        time_frequency=data_settings['time']['time_frequency'],
        time_rounding=data_settings['time']['time_rounding']
    )
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Driver and method of static datasets
    driver_data_static = DriverStatic(
        src_dict=data_settings['data']['static']['source'],
        dst_dict=data_settings['data']['static']['destination'],
        alg_template_tags=data_settings['algorithm']['template']
    )
    static_data_collection = driver_data_static.organize_static()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Iterate over time chunk(s)
    for time_reference, time_idx_group in time_chunks.items():

        # -------------------------------------------------------------------------------------
        # Driver and method of dynamic datasets
        driver_data_dynamic = DriverDynamic(
            time_reference, time_period=time_idx_group,
            static_data_collection=static_data_collection,
            src_dict=data_settings['data']['dynamic']['source'],
            anc_dict=data_settings['data']['dynamic']['ancillary'],
            dst_dict=data_settings['data']['dynamic']['destination'],
            alg_ancillary=data_settings['algorithm']['ancillary'],
            alg_template_tags=data_settings['algorithm']['template'],
            flag_cleaning_dynamic_data=data_settings['algorithm']['flags']['cleaning_dynamic_data'],
            flag_cleaning_dynamic_ancillary=data_settings['algorithm']['flags']['cleaning_dynamic_ancillary'],
            flag_cleaning_dynamic_tmp=data_settings['algorithm']['flags']['cleaning_dynamic_tmp'])

        driver_data_dynamic.organize_dynamic_data()
        driver_data_dynamic.dump_dynamic_data()
        driver_data_dynamic.clean_dynamic_tmp()
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    alg_time_elapsed = round(time.time() - alg_time_start, 1)

    log_stream.info(' ')
    log_stream.info('[' + project_name + ' ' + alg_type + ' - ' + alg_name + ' (Version ' + alg_version +
                    ' - Release ' + alg_release + ')]')
    log_stream.info(' ==> TIME ELAPSED: ' + str(alg_time_elapsed) + ' seconds')
    log_stream.info(' ==> ... END')
    log_stream.info(' ==> Bye, Bye')
    log_stream.info(' ============================================================================ ')
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to fill path names
def fill_script_settings(data_settings, domain):
    path_settings = {}

    for k, d in data_settings['path'].items():
        for k1, strValue in d.items():
            if isinstance(strValue, str):
                if '{' in strValue:
                    strValue = strValue.replace('{domain}', domain)
            path_settings[k1] = strValue

    return path_settings
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get script argument(s)
def get_args():
    parser_handle = argparse.ArgumentParser()
    parser_handle.add_argument('-settings_file', action="store", dest="alg_settings")
    parser_handle.add_argument('-time', action="store", dest="alg_time")
    parser_values = parser_handle.parse_args()

    if parser_values.alg_settings:
        alg_settings = parser_values.alg_settings
    else:
        alg_settings = 'configuration.json'

    if parser_values.alg_time:
        alg_time = parser_values.alg_time
    else:
        alg_time = None

    return alg_settings, alg_time

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to set logging information
def set_logging(logger_file='log.txt', logger_format=None):
    if logger_format is None:
        logger_format = '%(asctime)s %(name)-12s %(levelname)-8s ' \
                        '%(filename)s:[%(lineno)-6s - %(funcName)20s()] %(message)s'

    # Remove old logging file
    if os.path.exists(logger_file):
        os.remove(logger_file)

    # Set level of root debugger
    logging.root.setLevel(logging.DEBUG)

    # Open logging basic configuration
    logging.basicConfig(level=logging.DEBUG, format=logger_format, filename=logger_file, filemode='w')

    # Set logger handle
    logger_handle_1 = logging.FileHandler(logger_file, 'w')
    logger_handle_2 = logging.StreamHandler()
    # Set logger level
    logger_handle_1.setLevel(logging.DEBUG)
    logger_handle_2.setLevel(logging.DEBUG)
    # Set logger formatter
    logger_formatter = logging.Formatter(logger_format)
    logger_handle_1.setFormatter(logger_formatter)
    logger_handle_2.setFormatter(logger_formatter)

    # Add handle to logging
    logging.getLogger('').addHandler(logger_handle_1)
    logging.getLogger('').addHandler(logger_handle_2)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# -------------------------------------------------------------------------------------
