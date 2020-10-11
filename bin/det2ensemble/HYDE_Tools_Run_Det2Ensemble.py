#!/usr/bin/python3

"""
Hyde Tools - Det2Ensemble Converter

__date__ = '20190928'
__version__ = '1.0.0'
__author__ = 'Fabio Delogu (fabio.delogu@cimafoundation.org'
__library__ = 'HyDE'

General command line:
python3 HYDE_Tools_Run_Det2Ensemble.py -settings_file hyde_configuration_run_det2ensemble.json -time YYYYMMDDHHMM

Version:
20190928 (1.0.0) --> HyDE package
"""
# ----------------------------------------------------------------------------------------------------------------------
# Library
import logging
import json
import os
import collections
import argparse
import time

import pandas as pd
import numpy as np

from datetime import datetime
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Algorithm information
alg_name = 'HYDE TOOLS - DET2ENSEMBLE CONVERTER'
alg_version = '1.0.0'
alg_release = '2019-09-28'
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Script Main
def main():

    # ----------------------------------------------------------------------------------------------------------------------
    # Set log
    set_log()
    # ----------------------------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------------------
    # Info algorithm
    logging.info(' ============================================================================ ')
    logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_version + ')')
    logging.info(' ==> START ... ')
    logging.info(' ')

    # Time algorithm information
    alg_time_start = time.time()
    # ----------------------------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------------------
    # Get algorithm argument(s)
    script_name, config_file, time_arg = get_args()

    # Get generic information
    info_run, info_static, info_dynamic = file_configuration(config_file)
    # ----------------------------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------------------
    # Get section, time and ensemble(s) information
    section_info = file_section(os.path.join(info_static['folder_section'], info_static['file_section']))
    time_info = get_time(info_run['time'])
    ensemble_n_exp = get_ensemble(n_end=info_run['ensemble'])
    template_info = info_dynamic['template']

    # Define input and outcome file(s)
    file_raw_in = os.path.join(info_dynamic['input']['folder_discharge'], info_dynamic['input']['file_discharge'])
    file_raw_out = os.path.join(info_dynamic['outcome']['folder_discharge'], info_dynamic['outcome']['file_discharge'])
    # ----------------------------------------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Iterate over section(s)
    file_out_def = None
    for section_data in section_info:

        # ----------------------------------------------------------------------------------------------------------------------
        # Get section name
        section_name = get_section_name(section_data[2], section_data[3])
        # Info section starting
        logging.info(' ===> Section  ' + section_name + ' ... ')

        # Iterate over ensemble(s)
        file_out_header = None
        file_out_data_obs = None
        file_out_data_mod = None
        for ensemble_id in ensemble_n_exp:

            # Get ensemble number
            ensemble_name = template_info['ensemble'].format(ensemble_id)
            logging.info(' ====> Get data ensemble  ' + ensemble_name + ' ... ')

            # Define input and outcome template(s)
            template_in_values = {'datetime_input': time_info, 'sub_path_time': time_info,
                                  'ensemble': ensemble_name, 'section': section_name}
            template_out_values = {'datetime_outcome': time_info, 'sub_path_time': time_info,
                                   'ensemble': ensemble_name, 'section': section_name}

            file_in_def = fill_tags2string(file_raw_in, template_info, template_in_values)
            file_out_def = fill_tags2string(file_raw_out, template_info, template_out_values)

            # Get data
            if os.path.exists(file_in_def):
                file_in_header, file_in_data_obs, file_in_data_mod = file_discharge_det(file_in_def)

                if file_out_header is None:
                    file_out_header = file_in_header
                if file_out_data_obs is None:
                    file_out_data_obs = file_in_data_obs
                if file_out_data_mod is None:
                    file_out_data_mod = []

                file_out_data_mod.append(file_in_data_mod)

                logging.info(' ====> Get data ensemble  ' + ensemble_name + ' ... DONE')

            else:
                logging.warning(' ====> Get data ensemble  ' + ensemble_name + ' ... SKIPPED! Data not available!')

        # ----------------------------------------------------------------------------------------------------------------------

        # ----------------------------------------------------------------------------------------------------------------------
        # Define outcome file and save data
        if file_out_def is not None:
            folder_out_def, file_name_out_def = os.path.split(file_out_def)
            if os.path.exists(file_out_def):
                os.remove(file_out_def)

            if not os.path.exists(folder_out_def):
                os.makedirs(folder_out_def)

            # Info dump data starting
            logging.info(' ====> Save data ... ')

            # Compute ensemble n
            ensemble_n_cmp = file_out_data_mod.__len__()

            if ensemble_n_exp != ensemble_n_cmp:
                logging.warning(' =====> Ensemble(s) found < Ensemble(s) expected')

            # Save data
            file_discharge_ens(file_out_def, file_out_data_obs, file_out_data_mod,
                               file_out_header['DateMeteoModel'],
                               file_out_header['DateStart'],
                               file_out_header['Temp.Resolution'],
                               ensemble_n_cmp,
                               ensemble_name='ensemble_rfarm')
            # Info dump data ending
            logging.info(' ====> Save data ... DONE')

            # Info section ending
            logging.info(' ===> Section  ' + section_name + ' ... DONE')
        else:
            # Info section ending
            logging.warning(' ===> Section  ' + section_name + ' ... FAILED! All data are undefined!')
        # ----------------------------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------------------
    # Info algorithm
    alg_time_elapsed = round(time.time() - alg_time_start, 1)

    logging.info(' ')
    logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_version + ')')
    logging.info(' ==> TIME ELAPSED: ' + str(alg_time_elapsed) + ' seconds')
    logging.info(' ==> ... END')
    logging.info(' ==> Bye, Bye')
    logging.info(' ============================================================================ ')
    # ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to dump ensemble discharge file
def file_discharge_ens(file_name, file_data_obs, file_data_mod,
                       time_now, time_from, time_resolution,

                       ensemble_n, ensemble_name='ensemble_rfarm'):

    # Convert array from float to string
    list_data_obs = [file_data_obs.tolist()][0]

    # Save update information
    data_ws = {'line_01': 'Procedure=' + str(ensemble_name) + ' \n',
               'line_02': 'DateMeteoModel=' + str(time_now) + ' \n',
               'line_03': 'DateStart=' + str(time_from) + ' \n',
               'line_04': 'Temp.Resolution=' + str(time_resolution) + ' \n',
               'line_05': 'SscenariosNumber=' + str(int(ensemble_n)) + ' \n',
               'line_06': (' '.join(map(str, list_data_obs))) + ' \n'}

    # Iterate over ensemble(s)
    ensemble_format = '{:02d}'
    for ensemble_i in range(0, ensemble_n):
        ensemble_line = 'line_' + ensemble_format.format(ensemble_i + 7)

        arr_data_mod = file_data_mod[ensemble_i]
        list_data_mod = [arr_data_mod.tolist()][0]

        data_ws[ensemble_line] = (' '.join(map(str, list_data_mod))) + ' \n'

    # Dictionary sorting
    data_ws_ord = collections.OrderedDict(sorted(data_ws.items()))

    # Open ASCII file (to save all data)
    file_handler = open(file_name, 'w')

    # Write data in ASCII file
    file_handler.writelines(data_ws_ord.values())
    # Close ASCII file
    file_handler.close()
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to read deterministic discharge
def file_discharge_det(file_name, header_delimiter='='):

    # Get handle
    file_handle = open(file_name, 'r')

    # Read header
    file_header = {
        "Procedure": file_handle.readline().split(header_delimiter)[1].strip(),
        "DateMeteoModel": file_handle.readline().split(header_delimiter)[1].strip(),
        "DateStart": file_handle.readline().split(header_delimiter)[1].strip(),
        "Temp.Resolution": int(file_handle.readline().split(header_delimiter)[1]),
        "SscenariosNumber": int(file_handle.readline().split(header_delimiter)[1]),
    }

    # Read data
    file_data = np.loadtxt(file_handle, skiprows=0)
    file_data_obs = file_data[0]
    file_date_mod = file_data[1]

    return file_header, file_data_obs, file_date_mod
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to add time in a unfilled string (path or filename)
def fill_tags2string(string_raw, tags_format=None, tags_filling=None):

    apply_tags = False
    if string_raw is not None:
        for tag in list(tags_format.keys()):
            if tag in string_raw:
                apply_tags = True
                break

    if apply_tags:

        for tag_key, tag_value in tags_format.items():
            tag_key = '{' + tag_key + '}'
            if tag_value is not None:
                string_filled = string_raw.replace(tag_key, tag_value)
                string_raw = string_filled

        for tag_format_name, tag_format_value in list(tags_format.items()):

            if tag_format_name in list(tags_filling.keys()):
                tag_filling_value = tags_filling[tag_format_name]
                if tag_filling_value is not None:

                    if isinstance(tag_filling_value, datetime):
                        tag_filling_value = tag_filling_value.strftime(tag_format_value)

                    string_filled = string_filled.replace(tag_format_value, tag_filling_value)

        string_filled = string_filled.replace('//', '/')
        return string_filled
    else:
        return string_raw
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to get section name
def get_section_name(section_str1, section_str2):
    return section_str1.lower() + '_' + section_str2.lower()
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to get ensemble information
def get_ensemble(n_start=1, n_end=1):
    n_range = np.arange(n_start, n_end + 1, 1)
    n_ens = [i for i in n_range]
    return n_ens
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to parser file time
def get_time(time_str):
    return pd.Timestamp(time_str)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to get argument(s)
def get_args():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-settings_file', action="store", dest="settings_file")
    args_parser.add_argument('-time', action="store", dest="time_arg")
    args_values = args_parser.parse_args()

    script_name = args_parser.prog

    if 'settings_file' in args_values:
        settings_file = args_values.settings_file
    else:
        settings_file = 'hyde_configuration_run_det2ensemble.json'

    if 'time_arg' in args_values:
        time_arg = args_values.time_arg
    else:
        time_arg = None

    return script_name, settings_file, time_arg
# ----------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to set logging information
def set_log(logger_file='log.txt',
            logger_format='%(asctime)s %(name)-12s %(levelname)-8s %(filename)s:[%(lineno)-6s - '
                          '%(funcName)20s()] %(message)s'):

    # Remove old logging file
    if os.path.exists(logger_file):
        os.remove(logger_file)

    # Open logging basic configuration
    logging.basicConfig(level=logging.INFO,
                        format=logger_format,
                        filename=logger_file,
                        filemode='w')

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


# ----------------------------------------------------------------------------------------------------------------------
# Method to parser file section in ascii format
def file_section(file_name):
    file_handle = open(file_name, 'r')
    section_info = []
    for file_line in file_handle.readlines():
        file_line = file_line.strip()
        file_cols = file_line.split()
        section_info.append(file_cols)
    return section_info
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Method to parser configuration file
def file_configuration(config_file):
    with open(config_file) as config_handle:
        config_info = json.load(config_handle)
    info_run = config_info['info_run']
    info_static = config_info['info_static']
    info_dynamic = config_info['info_dynamic']

    return info_run, info_static, info_dynamic
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------------------------------------------------
