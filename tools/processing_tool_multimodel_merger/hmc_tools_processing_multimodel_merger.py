# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HMC tools - Merge multimodel results

__date__ = '20231027'
__version__ = '1.0.1'
__author__ = 'Andrea Libertino (andrea.libertino@cimafoundation.org')
__library__ = 'HMC'

General command line:
python3 HMC_calibration -settings_file "hmc_tools_multimodel_merger.py" -time "HHHH-MM-DD HH:MM"

20230919 (1.0.1) -->    Add support possibility of providing domain as input argument
20230919 (1.0.0) -->    Beta release
"""
# -------------------------------------------------------------------------------------
import xarray as xr
import glob
import sys
import os
from argparse import ArgumentParser
import logging
import time
import json
import datetime as dt
from copy import deepcopy
import pandas as pd
import numpy as np

# -------------------------------------------------------------------------------------

# Algorithm information
alg_name = 'HMC tools - Merge multimodel results'
alg_version = '1.0.1'
alg_release = '2023-10-27'
# Algorithm parameter(s)
time_format = '%Y%m%d%H%M'
# -------------------------------------------------------------------------------------
# Script main

def main():
    # -------------------------------------------------------------------------------------
    # Get algorithm settings
    alg_settings, alg_time, alg_domain = get_args()

    # Set algorithm settings
    data_settings = read_file_json(alg_settings)
    if alg_domain is None:
        domain = data_settings["algorithm"]["domain"]
    else:
        domain = alg_domain

    # Set algorithm logging
    os.makedirs(data_settings['data']['log']['folder'], exist_ok=True)
    set_logging(logger_file=os.path.join(data_settings['data']['log']['folder'], data_settings['data']['log']['filename']).format(domain=domain))

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    logging.info(' ============================================================================ ')
    logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
    logging.info(' ==> START ... ')
    logging.info(' ')

    start_time = time.time()

    time_run = dt.datetime.strptime(alg_time, '%Y-%m-%d %H:%M')
    logging.info(" --> Algorithm time: " + alg_time)

    logging.info(" --> Make folders...")
    template_filled = fill_template(data_settings["algorithm"]["template"], time_run)
    template_filled["domain"] = domain
    outcome_fld = data_settings["data"]["dynamic"]["outcome"]["folder"].format(**template_filled)
    os.makedirs(outcome_fld, exist_ok=True)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Read static data
    logging.info(" --> Read static data...")
    section_file = data_settings["data"]["static"]["section_file"].format(**template_filled)
    sections = read_section(section_file=section_file)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Read model outputs
    logging.info(" --> Read model outputs...")
    missing_series = False
    results = {}
    collections = {}

    # Loop through the models
    for model in data_settings["data"]["dynamic"]["model_output"].keys():
        logging.info(" ---> Model: " + model)
        model_outcome_fld = data_settings["data"]["dynamic"]["model_output"][model].format(**template_filled)

        # Loop through the sections
        for section,basin in zip(sections["section"], sections["basin"]):
            # Check existance of the collection for the section
            try:
                series, collect = read_discharge_collection(file_path=model_outcome_fld, file_name=None, section_name=section, basin_name=basin, run_date=time_run)
            except FileNotFoundError:
                logging.warning(" ----> File not found for section " + section + " and basin " + basin)
                series = None
                missing_series = True

            if series is not None:
                # If this is the first model, create the dataframe for the section
                if section not in results.keys():
                    results[section] = series
                    results[section].columns = [model]
                    collections[section] = collect
                # Else check if other models has same time span, if not fill with -9999
                else:
                    if len(results[section].index) != len(series.index):
                        index = results[section].index.union(series.index)
                        results[section] = results[section].reindex(index=index, fill_value=-9999)
                        results[section][model] = series
                    else:
                        results[section][model] = series
            else:
                if section in results.keys():
                    results[section] = pd.DataFrame(index=results[section].index, columns=[model], data=-9999)

    for section in results.keys():
        for model in data_settings["data"]["dynamic"]["model_output"].keys():
            if model not in results[section].columns:
                results[section][model] = -9999

    logging.info(" --> Read model outputs...DONE")
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Write outputs
    logging.info(" --> Write outputs...")
    for section, basin in zip(sections["section"], sections["basin"]):
        if section in results.keys():
            date_string = time_run.strftime("%Y%m%d%H%M")
            file_name = "hydrograph_" + section + "_" + basin + "_" + date_string + ".json"
            file_path = os.path.join(outcome_fld, file_name)
            with open(file_path, 'w') as f:
                f.write('{')
                for key in collections[section].keys():
                    if "time_series" not in key and key != "time_period":
                        f.write('\n"' + key + '": "' + str(collections[section][key]) + '",')
                for model in data_settings["data"]["dynamic"]["model_output"].keys():
                    f.write('\n"time_series_discharge_simulated-' + model + '": "')
                    f.write(','.join([str(i) for i in np.nan_to_num(results[section][model].values.flatten(), nan=-9999)]))
                    f.write('",')
                f.write('\n"time_period": "')
                f.write(','.join([i.strftime("%Y-%m-%d %H:%M") for i in results[section].index]))
                f.write('"\n}')
                logging.info(" ---> Write file: " + file_name + "...DONE")
        else:
            continue
            logging.info(" ---> Write file: " + file_name + "...SKIPPED")

    # -------------------------------------------------------------------------------------
    # Info algorithm
    time_elapsed = round(time.time() - start_time, 1)

    if missing_series:
        if data_settings["algorithm"]["flags"]["exit_with_error_if_missing_series"]:
            logging.warning("--> WARNING! Some series are missing! Exit with error!")
        else:
            logging.warning("--> WARNING! Some series are missing but the script run succesful!")

    logging.info(' ')
    logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
    logging.info(' ==> TIME ELAPSED: ' + str(time_elapsed) + ' seconds')
    logging.info(' ==> ... END')
    logging.info(' ==> Bye, Bye')
    logging.info(' ============================================================================ ')

    if missing_series is True and data_settings["algorithm"]["flags"]["exit_with_error_if_missing_series"] is True:
        sys.exit(1)
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to read file json
def read_file_json(file_name):
    env_ws = {}
    for env_item, env_value in os.environ.items():
        env_ws[env_item] = env_value

    with open(file_name, "r") as file_handle:
        json_block = []
        for file_row in file_handle:

            for env_key, env_value in env_ws.items():
                env_tag = '$' + env_key
                if env_tag in file_row:
                    env_value = env_value.strip("'\\'")
                    file_row = file_row.replace(env_tag, env_value)
                    file_row = file_row.replace('//', '/')

            # Add the line to our JSON block
            json_block.append(file_row)

            # Check whether we closed our JSON block
            if file_row.startswith('}'):
                # Do something with the JSON dictionary
                json_dict = json.loads(''.join(json_block))
                # Start a new block
                json_block = []

    return json_dict
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get script argument(s)
def get_args():
    parser_handle = ArgumentParser()
    parser_handle.add_argument('-settings_file', action="store", dest="alg_settings")
    parser_handle.add_argument('-time', action="store", dest="alg_time")
    parser_handle.add_argument('-domain', action="store", dest="alg_domain")
    parser_values = parser_handle.parse_args()

    if parser_values.alg_settings:
        alg_settings = parser_values.alg_settings
    else:
        alg_settings = 'configuration.json'

    if parser_values.alg_time:
        alg_time = parser_values.alg_time
    else:
        alg_time = None

    if parser_values.alg_domain:
        alg_domain = parser_values.alg_domain
    else:
        alg_domain = None

    return alg_settings, alg_time, alg_domain
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
    logging.root.setLevel(logging.INFO)

    # Open logging basic configuration
    logging.basicConfig(level=logging.INFO, format=logger_format, filename=logger_file, filemode='w')

    # Set logger handle
    logger_handle_1 = logging.FileHandler(logger_file, 'w')
    logger_handle_2 = logging.StreamHandler()
    # Set logger level
    logger_handle_1.setLevel(logging.INFO)
    logger_handle_2.setLevel(logging.INFO)
    # Set logger formatter
    logger_formatter = logging.Formatter(logger_format)
    logger_handle_1.setFormatter(logger_formatter)
    logger_handle_2.setFormatter(logger_formatter)

    # Add handle to logging
    logging.getLogger('').addHandler(logger_handle_1)
    logging.getLogger('').addHandler(logger_handle_2)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Function for fill a dictionary of templates
def fill_template(templates, time_now):
    empty_template = deepcopy(templates)
    templated_filled = {}
    for key in empty_template.keys():
        templated_filled[key] = time_now.strftime(empty_template[key])
    return templated_filled
# -------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Function for read section file
def read_section(section_file = None, column_labels = None, sep="\s+", column_names=["r_HMC","c_HMC","basin","section"], format='tabular'):
    if format == 'tabular':
        section_df = pd.read_csv(section_file, sep=sep, header=None)

        if len(section_df.columns) > len(column_names):
            logging.warning(' ---> WARNING! Section files has ' + str(len(section_df.columns)) + ' columns!')
            logging.info(' ---> First  ' + str(len(column_names)) + ' columns are interpreted as ' + ','.join(column_names) + ', others are ignored!')
            column_names.extend(['']*(len(section_df.columns)-len(column_names)))
        if len(section_df.columns) < len(column_names):
            logging.error(' ---> ERROR! Section files has ' + str(len(section_df.columns)) + ' columns, cannot interpret as standard HMC section file!')
            raise IOError("Verify your section file or provide a personal column setup!")

        section_df.columns=column_names

    return section_df
# -------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Method to read file json
def read_file_json(file_name):
    env_ws = {}
    for env_item, env_value in os.environ.items():
        env_ws[env_item] = env_value

    with open(file_name, "r") as file_handle:
        json_block = []
        for file_row in file_handle:

            for env_key, env_value in env_ws.items():
                env_tag = '$' + env_key
                if env_tag in file_row:
                    env_value = env_value.strip("'\\'")
                    file_row = file_row.replace(env_tag, env_value)
                    file_row = file_row.replace('//', '/')

            # Add the line to our JSON block
            json_block.append(file_row)

            # Check whether we closed our JSON block
            if file_row.startswith('}'):
                # Do something with the JSON dictionary
                json_dict = json.loads(''.join(json_block))
                # Start a new block
                json_block = []

    return json_dict
# -------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Function for read Continuum output in json format
def read_discharge_collection(file_path, file_name=None, section_name=None, basin_name = None, run_date=None):
    if file_name is None:
        if all((section_name, basin_name, run_date)) is not None:
            if isinstance(run_date, dt.datetime):
                date_string = run_date.strftime("%Y%m%d%H%M")
            elif isinstance(run_date, str):
                date_string = run_date
            else:
                logging.error(' ---> ERROR! Only datetime and sting date format are supported!')
                raise NotImplementedError
            file_name = "hydrograph_" + section_name + "_" + basin_name + "_" + date_string + ".json"
        elif any((section_name, basin_name, run_date)) is not None:
            logging.error(' ---> ERROR! You should specify either filename or section name + basin + run date!')
            raise ValueError
    collect = read_file_json(os.path.join(file_path, file_name))
    series = np.asarray(collect['time_series_discharge_simulated'].split(','), dtype=np.float32)[1:]
    date_range_str = collect['time_period'].split(',')
    date_range = [dt.datetime.strptime(i, "%Y-%m-%d %H:%M") for i in date_range_str][1:]
    series_hmc = pd.DataFrame(data=series, index=date_range)

    return series_hmc, collect
# -------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------