"""
Library Features:

Name:          lib_utils_io
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20221019'
Version:       '2.0.0'
"""
# -------------------------------------------------------------------------------------
# Library
import logging
import os

from copy import deepcopy

from lib_data_io import read_file_json, write_file_json
from lib_utils_system import set_dict_value, make_folder
from lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to organize configuration file
def organize_configuration_file(script_args, tag_arg_template='template', tag_arg_runtime='runtime',
                                script_path_default=None):

    app_configuration_file_template, app_configuration_file_runtime = {}, {}
    for script_key, script_file_default in script_args.items():
        if tag_arg_template in script_key:
            script_key_root, script_key_type = script_key.split(tag_arg_template)
            script_key_root = script_key_root.strip(":")
            script_file_selected = search_configuration_file(script_file_default,
                                                             file_location_default=script_path_default)
            app_configuration_file_template[script_key_root] = script_file_selected
        elif tag_arg_runtime in script_key:
            script_key_root, script_key_type = script_key.split(tag_arg_runtime)
            script_key_root = script_key_root.strip(":")
            app_configuration_file_runtime[script_key_root] = script_file_default
        else:
            log_stream.error(' ===> Tag "' + script_key + '" to select case is not allowed')
            raise NotImplementedError('Case not implemented yet')

    return app_configuration_file_template, app_configuration_file_runtime
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to search configuration file in default location (if needed)
def search_configuration_file(file_path_settings, file_location_default=None):
    if os.path.exists(file_path_settings):
        file_path_select = deepcopy(file_path_settings)
    else:
        if file_location_default:
            log_stream.warning(' ===> Configuration file "' + file_path_settings +
                               '" does not exist. Try to use the default location "' + file_location_default + '"')
            file_location_settings, file_name_settings = os.path.split(file_path_settings)
            file_path_select = os.path.join(file_location_default, file_name_settings)
        else:
            log_stream.error(' ===> Configuration file "' + file_path_settings +
                             '" does not exist. The default location must be defined by a string path')
            raise RuntimeError('The default location is defined by NoneType.')

    if not os.path.exists(file_path_select):
        log_stream.error(' ===> Configuration file "' + file_path_select + '" does not exist.')
        raise FileNotFoundError('File not found. Try to change the location or the name of the file.')

    return file_path_select
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read configuration file
def read_configuration_file(app_configuration_file):

    app_configuration_obj = {}
    for app_key, app_file in app_configuration_file.items():

        if os.path.exists(app_file):
            app_obj = read_file_json(app_file)
        else:
            log_stream.error(' ===> Configuration file "' + app_file + '" does not exist')
            raise IOError('File is needed by the algorithm')

        app_configuration_obj[app_key] = app_obj

    return app_configuration_obj
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to connect keys (reference and list)
def connect_keys(key_ref, key_list, key_sep=':'):
    key_ref_root, key_ref_type = key_ref.split(key_sep)
    key_other_sel = None
    for key_id, key_other in enumerate(key_list):
        key_other_ref, key_other_type = key_other.split(key_sep)

        if key_ref_type == key_other_type:
            key_other_sel = key_list[key_id]
            break

    if key_other_sel is None:
        log_stream.error(' ===> Key reference "' + key_ref + '" is not available in the searching list')
        raise RuntimeError('The key reference must have the connection in the key list')

    return key_other_sel
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to link variable(s) and lut(s) of configuration file
def link_configuration_file(
        app_variable_obj, app_lut_obj,
        tag_var_2_lut='link_variable_2_lut', tag_lut_2_var='link_lut_2_variable'):

    for app_var_key, app_var_fields in app_variable_obj.items():

        app_lut_key = connect_keys(app_var_key, list(app_lut_obj.keys()))
        app_lut_fields = app_lut_obj[app_lut_key]

        app_var_list, app_lut_list = list(app_var_fields.keys()), list(app_lut_fields.keys())
        app_common_list = sorted(list(set(app_var_list + app_lut_list)))

        var_key_list, var_value_list = [], []
        for app_var_name in app_var_list:

            if app_var_name in app_lut_list:
                app_var_check = True
            else:
                app_var_check = False
                log_stream.warning(' ===> Variable Key "' + app_var_name +
                                   '" is not available in the lut key collection.')

            var_key_list.append(app_var_name)
            var_value_list.append(app_var_check)

        lut_key_list, lut_value_list = [], []
        for app_var_name in app_lut_list:

            if app_var_name in app_var_list:
                app_var_check = True
            else:
                app_var_check = False
                log_stream.warning(' ===> Lut Key "' + app_var_name +
                                   '" is not available in the variable key collection.')

            lut_key_list.append(app_var_name)
            lut_value_list.append(app_var_check)

        app_link_var = {}
        for app_common_name in app_common_list:
            app_link_var[app_common_name] = {}
            if app_common_name in var_key_list:
                var_key_id = var_key_list.index(app_common_name)
                app_link_var[app_common_name] = var_value_list[var_key_id]
            else:
                app_link_var[app_common_name] = None

        app_link_lut = {}
        for app_common_name in app_common_list:
            app_link_lut[app_common_name] = {}
            if app_common_name in lut_key_list:
                lut_key_id = lut_key_list.index(app_common_name)
                app_link_lut[app_common_name] = lut_value_list[lut_key_id]
            else:
                app_link_lut[app_common_name] = None

        app_link_obj = {tag_var_2_lut: app_link_var, tag_lut_2_var: app_link_lut}

        return app_link_obj
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to fill configuration file
def fill_configuration_file(app_configuration_obj_in, app_lut_obj, app_var_obj):

    app_configuration_obj_out = {}
    for app_config_key, app_config_fields in app_configuration_obj_in.items():

        app_lut_key = connect_keys(app_config_key, list(app_lut_obj.keys()))
        app_lut_fields = app_lut_obj[app_lut_key]

        app_var_key = connect_keys(app_config_key, list(app_var_obj.keys()))
        app_var_fields = app_var_obj[app_var_key]

        for lut_key, lut_value in app_lut_fields.items():

            if lut_key in list(app_var_fields.keys()):
                var_value = app_var_fields[lut_key]

                if lut_value is not None:
                    app_config_fields = set_dict_value(app_config_fields, lut_value, var_value, False)

            else:
                log_stream.warning(' ===> Key "' + lut_key + '" is expected but not defined in the variable group.')

        app_configuration_obj_out[app_config_key] = app_config_fields

    return app_configuration_obj_out
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write configuration file
def write_configuration_file(app_entrypoint_obj_file, app_entrypoint_obj_datasets):

    for app_entrypoint_key, app_entrypoint_path in app_entrypoint_obj_file.items():

        if app_entrypoint_key in list(app_entrypoint_obj_datasets.keys()):

            app_entrypoint_fields = app_entrypoint_obj_datasets[app_entrypoint_key]

            app_entrypint_folder, app_entrypoint_file = os.path.split(app_entrypoint_path)
            make_folder(app_entrypint_folder)
            write_file_json(app_entrypoint_path, app_entrypoint_fields)

        else:
            log_stream.error(' ===> Entrypoint key "' + app_entrypoint_key +
                             '" is not available in the entrypoint datasets')
            raise RuntimeError('The entrypoint key do not refer to a valid datasets')

    return True
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to filter entrypoint settings
def filter_unnecessary_keys(obj_entrypoint_raw, excluded_keys=None):
    if excluded_keys is None:
        excluded_keys = ['__comment__', '_comment', '_comment_']
    obj_entrypoint_filtered = {}
    for obj_key, obj_field in obj_entrypoint_raw.items():
        if obj_key not in excluded_keys:
            obj_entrypoint_filtered[obj_key] = obj_field
    return obj_entrypoint_filtered
# -------------------------------------------------------------------------------------
