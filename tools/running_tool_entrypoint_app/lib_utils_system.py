"""
Library Features:

Name:          lib_utils_system
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20221019'
Version:       '2.0.0'
"""
# -------------------------------------------------------------------------------------
# Library
import logging
import os
import numpy as np
from datetime import datetime

from lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to make folder
def make_folder(path_folder_list, sep_string='%'):

    if isinstance(path_folder_list, str):
        path_folder_list = [path_folder_list]

    for path_folder in path_folder_list:
        if path_folder is not None:
            if sep_string in path_folder:
                path_folder_root, path_dyn = path_folder.split(sep_string, 1)
            else:
                path_folder_root = path_folder

            if not os.path.exists(path_folder_root):
                os.makedirs(path_folder_root)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to add format(s) string (path or filename)
def fill_tags2string(string_raw, tags_format=None, tags_filling=None, tags_template='[TMPL_TAG_{:}]'):

    apply_tags = False
    if string_raw is not None:
        for tag in list(tags_format.keys()):

            if tag in string_raw:
                apply_tags = True
                break

    if apply_tags:

        string_filled = None
        tag_dictionary = {}
        for tag_id, (tag_key, tag_value) in enumerate(tags_format.items()):
            tag_key_tmp = '{' + tag_key + '}'
            if tag_value is not None:

                tag_id = tags_template.format(tag_id)
                tag_dictionary[tag_id] = {'key': None, 'type': None}

                if tag_key_tmp in string_raw:
                    tag_dictionary[tag_id] = {'key': tag_key, 'type': tag_value}
                    string_filled = string_raw.replace(tag_key_tmp, tag_id)
                    string_raw = string_filled
                else:
                    tag_dictionary[tag_id] = {'key': tag_key, 'type': None}

        dim_max = 1
        for tags_filling_values_tmp in tags_filling.values():
            if isinstance(tags_filling_values_tmp, list):
                dim_tmp = tags_filling_values_tmp.__len__()
                if dim_tmp > dim_max:
                    dim_max = dim_tmp

        string_filled_list = [string_filled] * dim_max

        string_filled_def, string_list_key, string_list_value, string_list_type = [], [], [], []
        for string_id, string_filled_step in enumerate(string_filled_list):

            for tag_dict_template, tag_dict_fields in tag_dictionary.items():
                tag_dict_key = tag_dict_fields['key']
                tag_dict_type = tag_dict_fields['type']

                if string_filled_step is not None and tag_dict_template in string_filled_step:
                    if tag_dict_type is not None:

                        if tag_dict_key in list(tags_filling.keys()):

                            value_filling_obj = tags_filling[tag_dict_key]

                            if isinstance(value_filling_obj, list):
                                value_filling = value_filling_obj[string_id]
                            else:
                                value_filling = value_filling_obj

                            string_filled_step = string_filled_step.replace(tag_dict_template, tag_dict_key)

                            if isinstance(value_filling, datetime):
                                tag_dict_value = value_filling.strftime(tag_dict_type)
                            elif isinstance(value_filling, (float, int)):
                                tag_dict_value = tag_dict_key.format(value_filling)
                            else:
                                tag_dict_value = value_filling

                            if tag_dict_value is None:
                                tag_dict_undef = '{' + tag_dict_key + '}'
                                string_filled_step = string_filled_step.replace(tag_dict_key, tag_dict_undef)

                            if tag_dict_value:
                                string_filled_step = string_filled_step.replace(tag_dict_key, tag_dict_value)
                                string_list_key.append(tag_dict_key)
                                string_list_value.append(tag_dict_value)
                                string_list_type.append(tag_dict_type)
                            else:
                                log_stream.warning(' ===> The key "' + tag_dict_key + '" for "' + string_filled_step +
                                                   '" is not correctly filled; the value is set to NoneType')

            string_filled_def.append(string_filled_step)

        if dim_max == 1:
            if string_filled_def[0]:
                string_filled_out = string_filled_def[0].replace('//', '/')
            else:
                string_filled_out = []
        else:
            string_filled_out = []
            for string_filled_tmp in string_filled_def:
                if string_filled_tmp:
                    string_filled_out.append(string_filled_tmp.replace('//', '/'))

        return string_filled_out, string_list_key, string_list_value, string_list_type
    else:
        string_list_key, string_list_value, string_list_type = [], [], []
        return string_raw, string_list_key, string_list_value, string_list_type
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
#  Method to set value in a defined dictionary
def set_dict_value(dic, keys, value, create_missing=True):
    d = dic
    for key in keys[:-1]:
        if key in d:
            d = d[key]
        elif create_missing:
            d = d.setdefault(key, {})
        else:
            return dic
    if keys[-1] in d or create_missing:
        d[keys[-1]] = value
    return dic
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get nested value
def get_dict_value(d, key, value=[]):

    for k, v in iter(d.items()):
        if isinstance(v, dict):
            if k == key:
                for kk, vv in iter(v.items()):
                    temp = [kk, vv]
                    value.append(temp)
            else:
                vf = get_dict_value(v, key, value)
                if isinstance(vf, list):
                    if vf:
                        vf_end = vf[0]
                    else:
                        vf_end = None
                elif isinstance(vf, np.ndarray):
                    vf_end = vf.tolist()
                else:
                    vf_end = vf
                if vf_end not in value:
                    if vf_end:
                        if isinstance(value, list):
                            value.append(vf_end)
                        elif isinstance(value, str):
                            value = [value, vf_end]
                    else:
                        pass
                else:
                    pass
        else:
            if k == key:
                if isinstance(v, np.ndarray):
                    value = v
                else:
                    value = v
    return value
# -------------------------------------------------------------------------------------
