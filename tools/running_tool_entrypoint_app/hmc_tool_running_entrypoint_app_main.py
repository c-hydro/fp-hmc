#!/usr/bin/python3

"""
HYDROLOGICAL MODEL CONTINUUM - Tool Entrypoint App

__date__ = '20221019'
__version__ = '2.0.0'
__author__ = 'Fabio Delogu (fabio.delogu@cimafoundation.org'
__library__ = 'hmc'

General command line:
python hmc_tool_running_entrypoint_app_main.py -settings_file configuration.json
"""

# -------------------------------------------------------------------------------------
# Complete library
import logging
import os
import sys
import time

from argparse import ArgumentParser

from lib_info_args import logger_name
from lib_utils_logging import define_logging_file, set_logging_file

from lib_utils_entrypoint_settings import read_entrypoint_settings, \
    parse_entrypoint_settings, organize_entrypoint_settings
from lib_utils_entrypoint_app import organize_entrypoint_app, filter_entrypoint_app
from lib_utils_entrypoint_variable import organize_entrypoint_variable
from lib_utils_entrypoint_time import organize_entrypoint_time

from lib_utils_io import organize_configuration_file, read_configuration_file, \
    fill_configuration_file, link_configuration_file, write_configuration_file

from lib_utils_cmd import compose_cmd, join_cmd, execute_cmd

# Logging
log_stream = logging.getLogger(logger_name)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Algorithm information
project_name = 'HMC'
alg_name = 'TOOL ENTRYPOINT APP'
alg_type = 'Model'
alg_version = '2.0.0'
alg_release = '2022-10-14'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Script Main
def main():

    # -------------------------------------------------------------------------------------
    # Get algorithm settings
    file_entrypoint_settings, file_entrypoint_path = get_args()

    # Read entrypoint generic object
    obj_entrypoint_generic = read_entrypoint_settings(file_entrypoint_settings)

    # Parse entrypoint settings, variable, app and lut object(s)
    obj_entrypoint_settings, \
        obj_entrypoint_app, obj_entrypoint_lut = parse_entrypoint_settings(obj_entrypoint_generic)

    # Define entrypoint variable(s)
    tmp_entrypoint_variable = organize_entrypoint_variable(obj_entrypoint_settings)
    # Define entrypoint time(s)
    app_entrypoint_time_now, app_entrypoint_variable = organize_entrypoint_time(tmp_entrypoint_variable)
    # Define entrypoint apps and log
    app_entrypoint_list, app_entrypoint_template, app_entrypoint_log = organize_entrypoint_settings(
        obj_entrypoint_settings, app_entrypoint_variable)

    # Define and set algorithm logging
    logger_entrypoint_file = define_logging_file(app_entrypoint_log)
    set_logging_file(logger_name=logger_name, logger_file=logger_entrypoint_file)
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
    # Iterate over application(s)
    for app_entrypoint_name in app_entrypoint_list:

        # -------------------------------------------------------------------------------------
        # Start part of entrypoint for the defined application
        log_stream.info(' ---> Application Entrypoint "' + app_entrypoint_name + '" ... ')

        # Organize entrypoint generic obj
        log_stream.info(' ----> Organize entrypoint generic object ... ')
        app_entrypoint_generic = organize_entrypoint_app(
            app_entrypoint_name, [obj_entrypoint_app, obj_entrypoint_lut])

        # End part of entrypoint for the defined application
        log_stream.info(' ----> Organize entrypoint generic object ... DONE')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Start part of entrypoint script object(s)
        log_stream.info(' ----> Organize entrypoint script object(s) ... ')

        # Organize entrypoint script settings
        app_entrypoint_script_settings = filter_entrypoint_app(
            app_entrypoint_generic,  tag_root_fields='app_script_settings',
            template_keys=app_entrypoint_template, template_values=app_entrypoint_variable, template_use=True)
        # Organize entrypoint script main
        app_entrypoint_script_main = filter_entrypoint_app(
            app_entrypoint_generic, tag_root_fields='app_script_main',
            template_keys=app_entrypoint_template, template_values=app_entrypoint_variable, template_use=True)
        # Organize entrypoint script args
        app_entrypoint_script_args = filter_entrypoint_app(
            app_entrypoint_generic, tag_root_fields='app_script_args',
            template_keys=app_entrypoint_template, template_values=app_entrypoint_variable, template_use=True)
        # Organize entrypoint script variable
        app_entrypoint_script_variable = filter_entrypoint_app(
            app_entrypoint_generic, tag_root_fields='app_script_variable',
            template_keys=app_entrypoint_template, template_values=app_entrypoint_variable, template_use=True)
        # Organize entrypoint look-up table
        app_entrypoint_lut = filter_entrypoint_app(
            app_entrypoint_generic, tag_root_fields='lookup_table_fields',
            template_keys=app_entrypoint_template, template_values=app_entrypoint_variable, template_use=False)
        # Check script variable and look-up table fields
        app_entrypoint_link = link_configuration_file(app_entrypoint_script_variable, app_entrypoint_lut)

        # End part of entrypoint script object(s)
        log_stream.info(' ----> Organize entrypoint script object(s) ... DONE')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Start part of entrypoint configuration file
        log_stream.info(' ----> Organize entrypoint configuration file(s)  ... ')

        # Get configuration file (template and runtime structure)
        app_entrypoint_file_config_template, \
            app_entrypoint_file_config_runtime = organize_configuration_file(app_entrypoint_script_args,
                                                                             script_path_default=file_entrypoint_path)
        # Read configuration file (template structure)
        app_entrypoint_obj_config_template = read_configuration_file(app_entrypoint_file_config_template)
        # Fill configuration file
        app_entrypoint_obj_config_runtime = fill_configuration_file(
            app_entrypoint_obj_config_template, app_entrypoint_lut, app_entrypoint_script_variable)
        # Write configuration file (runtime structure)
        write_configuration_file(app_entrypoint_file_config_runtime, app_entrypoint_obj_config_runtime)

        # End part of entrypoint configuration file
        log_stream.info(' ----> Organize entrypoint configuration file(s) ... DONE')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Start part of entrypoint command-line definition
        log_stream.info(' ----> Define entrypoint command-line ... ')
        # Compose application command-line parts
        app_entrypoint_cmd_obj = compose_cmd(app_entrypoint_script_settings,
                                             app_entrypoint_script_main, app_entrypoint_file_config_runtime,
                                             script_time=app_entrypoint_time_now, script_interpreter='python')
        # Join application command-line parts
        app_entrypoint_cmd_launcher = join_cmd(app_entrypoint_cmd_obj)
        # End part of entrypoint command-line definition
        log_stream.info(' ----> Define entrypoint command-line ... DONE')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Start part of entrypoint command-line execution
        log_stream.info(' ----> Execute entrypoint command-line ... ')
        # Execute application command-line
        execute_cmd(app_entrypoint_cmd_launcher)
        # End part of entrypoint command-line execution
        log_stream.info(' ----> Execute entrypoint command-line ... DONE')
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # End part of entrypoint for the defined application
        log_stream.info(' ---> Application Entrypoint "' + app_entrypoint_name + '" ... DONE')
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
# Method to get script argument(s)
def get_args():
    parser_handle = ArgumentParser()
    parser_handle.add_argument('-settings_file', action="store", dest="file_settings")
    parser_values = parser_handle.parse_args()

    if parser_values.file_settings:
        file_settings = parser_values.file_settings
    else:
        file_settings = 'configuration.json'

    file_path = os.path.dirname(os.path.realpath(sys.argv[0]))

    return file_settings, file_path
# -------------------------------------------------------------------------------------

def get_location():
    pass


# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------
