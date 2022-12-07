"""
Library Features:

Name:          lib_utils_entrypoint_app
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20221019'
Version:       '2.0.0'
"""
# -------------------------------------------------------------------------------------
# Library
import os
import logging

from copy import deepcopy

from lib_utils_system import fill_tags2string

template_file_path = ['folder_name', 'file_name']
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to organize entrypoint app
def filter_entrypoint_app(app_fields_generic, tag_root_fields='app_settings',
                          template_keys=None, template_values=None, template_use=True):

    app_fields_filtered = {}
    if tag_root_fields in list(app_fields_generic.keys()):
        app_fields_tmp = app_fields_generic[tag_root_fields]

        if isinstance(app_fields_tmp, dict):

            for key_obj, values_obj_raw in app_fields_tmp.items():

                if template_use:
                    if all(elem in values_obj_raw for elem in template_file_path):
                        folder_name = values_obj_raw[template_file_path[0]]
                        file_name = values_obj_raw[template_file_path[1]]
                        file_path = os.path.join(folder_name, file_name)
                        value_obj_def, tag_list_tmp, value_list_tmp, type_list_tmp = fill_tags2string(
                            file_path, template_keys, template_values)
                    else:

                        if isinstance(values_obj_raw, dict):
                            value_obj_def = {}
                            for value_key, value_data in values_obj_raw.items():

                                if value_data:
                                    if isinstance(value_data, bool):
                                        obj_def = deepcopy(value_data)
                                    elif isinstance(value_data, int):
                                        obj_def = deepcopy(value_data)
                                    elif isinstance(value_data, float):
                                        obj_def = deepcopy(value_data)
                                    elif isinstance(value_data, list):
                                        obj_list = deepcopy(value_data)

                                        obj_def = []
                                        for obj_step in obj_list:
                                            obj_tmp, tag_list_tmp, value_list_tmp, type_list_tmp = fill_tags2string(
                                                obj_step, template_keys, template_values)
                                            obj_def.append(obj_tmp)

                                    else:
                                        obj_tmp, tag_list_tmp, value_list_tmp, type_list_tmp = fill_tags2string(
                                            value_data, template_keys, template_values)
                                        if type_list_tmp.__len__() == 1 and type_list_tmp[0] == 'integer':
                                            obj_def = int(obj_tmp)
                                        elif type_list_tmp.__len__() == 1 and type_list_tmp[0] == 'float':
                                            obj_def = float(obj_tmp)
                                        else:
                                            obj_def = deepcopy(obj_tmp)
                                else:
                                    obj_def = deepcopy(value_data)
                                value_obj_def[value_key] = obj_def
                        elif isinstance(values_obj_raw, str):
                            value_obj_def = deepcopy(values_obj_raw)
                        elif isinstance(values_obj_raw, list):
                            value_obj_def = deepcopy(values_obj_raw)
                        else:
                            logging.error(' ===> Application obj must be "dictionary" or "string"')
                            raise NotImplementedError('Case not implemented yet')
                else:
                    value_obj_def = deepcopy(values_obj_raw)

                app_fields_filtered[key_obj] = value_obj_def

        else:
            logging.error(' ===> Application fields format must be a dictionary')
            raise NotImplementedError('Case not implemented yet')

    else:
        logging.warning(' ===> Application fields name "' + tag_root_fields +
                        '" is not available in the application generic obj. The related obj will be defined by NoneTye')
        app_fields_filtered = None

    return app_fields_filtered
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to organize entrypoint app
def organize_entrypoint_app(app_name, obj_entrypoint_list):
    if app_name:
        app_entrypoint_fields = {}
        for obj_entrypoint_step in obj_entrypoint_list:
            for obj_key, obj_fields in obj_entrypoint_step.items():
                if app_name in list(obj_fields.keys()):
                    app_fields = obj_fields[app_name]
                else:
                    app_fields = None
                app_entrypoint_fields[obj_key] = app_fields
    else:
        logging.error(' ===> Application name defined by NoneType')
        raise RuntimeError('Application name must a string')
    return app_entrypoint_fields
# -------------------------------------------------------------------------------------
