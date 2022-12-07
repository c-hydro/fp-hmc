"""
Library Features:

Name:          lib_utils_entrypoint_settings
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20221019'
Version:       '2.0.0'
"""
# -------------------------------------------------------------------------------------
# Library
import logging
import os

from lib_data_io import read_file_json
from lib_utils_io import filter_unnecessary_keys
from lib_info_args import logger_format

# Logging
log_fx = logging.getLogger(__name__)
log_fx.setLevel(logging.INFO)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter(logger_format)
log_handler.setFormatter(log_formatter)
log_fx.addHandler(log_handler)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read entrypoint settings
def read_entrypoint_settings(file_name):

    if os.path.exists(file_name):
        file_data = read_file_json(file_name)
    else:
        log_fx.error(' ===> Entrypoint configuration file "' + file_name + '" does not exist')
        raise FileNotFoundError('File not found')
    return file_data
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to organize entrypoint settings
def organize_entrypoint_settings(obj_entrypoint_settings, app_entrypoint_variable,
                                 tag_obj_version='version',
                                 tag_obj_app_name='application_name',
                                 tag_obj_app_template='application_variable_template',
                                 tag_obj_log='log',
                                 tag_run_path_root='run_path_root',
                                 tag_run_domain='run_domain', tag_run_time_now='run_time_now'):

    if tag_run_path_root in list(app_entrypoint_variable.keys()):
        run_path_root = app_entrypoint_variable[tag_run_path_root]
    else:
        run_path_root = None
    if tag_run_domain in list(app_entrypoint_variable.keys()):
        run_domain = app_entrypoint_variable[tag_run_domain]
    else:
        run_domain = None
    if tag_run_time_now in list(app_entrypoint_variable.keys()):
        run_time_now = app_entrypoint_variable[tag_run_time_now]
    else:
        run_time_now = None

    if tag_obj_version in list(obj_entrypoint_settings.keys()):
        _ = obj_entrypoint_settings[tag_obj_version]
    else:
        log_fx.error(' ===> Field "' + tag_obj_version + '" is not defined in the configuration file')
        raise RuntimeError('Field "' + tag_obj_version + '" must be defined')
    if tag_obj_app_name in list(obj_entrypoint_settings.keys()):
        obj_entrypoint_app_name = obj_entrypoint_settings[tag_obj_app_name]
    else:
        log_fx.error(' ===> Field "' + tag_obj_app_name + '" is not defined in the configuration file')
        raise RuntimeError('Field "' + tag_obj_app_name + '" must be defined')
    if tag_obj_app_template in list(obj_entrypoint_settings.keys()):
        obj_entrypoint_app_template = obj_entrypoint_settings[tag_obj_app_template]
    else:
        log_fx.error(' ===> Field "' + tag_obj_app_template + '" is not defined in the configuration file')
        raise RuntimeError('Field "' + tag_obj_app_template + '" must be defined')
    if tag_obj_log in list(obj_entrypoint_settings.keys()):
        obj_entrypoint_log = obj_entrypoint_settings[tag_obj_log]

        obj_entrypoint_template = {tag_run_path_root: run_path_root,
                                   tag_run_domain: run_domain, tag_run_time_now: run_time_now}
        if run_path_root is not None:
            for log_key, log_value in obj_entrypoint_log.items():
                log_filled = log_value.format(**obj_entrypoint_template)
                log_filled = os.path.normpath(log_filled)
                obj_entrypoint_log[log_key] = log_filled

    else:
        log_fx.error(' ===> Field "' + tag_obj_log + '" is not defined in the configuration file')
        raise RuntimeError('Field "' + tag_obj_log + '" must be defined')

    return obj_entrypoint_app_name, obj_entrypoint_app_template, obj_entrypoint_log
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# method to parse entrypoint settings
def parse_entrypoint_settings(obj_entrypoint_generic,
                              tag_obj_settings='docker_entrypoint_settings',
                              tag_obj_app="docker_entrypoint_app", tag_obj_lut='docker_entrypoint_lookup_table'):

    if tag_obj_settings in list(obj_entrypoint_generic.keys()):
        obj_entrypoint_tmp = obj_entrypoint_generic[tag_obj_settings]
        obj_entrypoint_settings = filter_unnecessary_keys(obj_entrypoint_tmp)
    else:
        log_fx.error(' ===> Field "' + tag_obj_settings + '" is not defined in the configuration file')
        raise RuntimeError('Field "' + tag_obj_settings + '" must be defined')

    if tag_obj_app in list(obj_entrypoint_generic.keys()):
        obj_entrypoint_tmp = obj_entrypoint_generic[tag_obj_app]
        obj_entrypoint_app = filter_unnecessary_keys(obj_entrypoint_tmp)
    else:
        log_fx.error(' ===> Field "' + tag_obj_app + '" is not defined in the configuration file')
        raise RuntimeError('Field "' + tag_obj_app + '" must be defined')

    if tag_obj_lut in list(obj_entrypoint_generic.keys()):
        obj_entrypoint_tmp = obj_entrypoint_generic[tag_obj_lut]
        obj_entrypoint_lut = filter_unnecessary_keys(obj_entrypoint_tmp)
    else:
        log_fx.error(' ===> Field "' + tag_obj_lut + '" is not defined in the configuration file')
        raise RuntimeError('Field "' + tag_obj_lut + '" must be defined')

    return obj_entrypoint_settings, obj_entrypoint_app, obj_entrypoint_lut
# -------------------------------------------------------------------------------------
