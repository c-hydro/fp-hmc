"""
Library Features:

Name:          lib_utils_system
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20211208'
Version:       '1.0.0'
"""

#######################################################################################
# Libraries
import os
from datetime import datetime
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to intersect dictionaries
def intersect_dicts(dict_a, dict_b):
    shared_keys = dict_a.keys() & dict_b.keys()
    dict_intersection = {k: dict_a[k] for k in shared_keys}
    return dict_intersection
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to find sub-folders
def find_folder(main_path, reverse=True):
    path_generator = os.walk(main_path)

    path_list = []
    for path_obj in path_generator:
        path_string = path_obj[0]
        path_list.append(path_string)

    if reverse:
        path_list.reverse()

    return path_list
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to make folder
def make_folder(path_folder):
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to flat list of list
def flat_list(lists):
    return [item for sublist in lists for item in sublist]
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert coupled list to dictionary
def convert_list2dict(list_keys, list_values):
    dictionary = {k: v for k, v in zip(list_keys, list_values)}
    return dictionary
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

    if string_raw is not None:
        if apply_tags:

            string_filled = None
            tag_dictionary = {}
            for tag_id, (tag_key, tag_value) in enumerate(tags_format.items()):
                tag_key_tmp = '{' + tag_key + '}'
                if tag_value is not None:

                    tag_id = tags_template.format(tag_id)
                    tag_dictionary[tag_id] = {'key': None, 'value': None}

                    if tag_key_tmp in string_raw:
                        tag_dictionary[tag_id] = {'key': tag_key, 'value': tag_value}
                        string_filled = string_raw.replace(tag_key_tmp, tag_id)
                        string_raw = string_filled
                    else:
                        tag_dictionary[tag_id] = {'key': tag_key, 'value': None}

            dim_max = 1
            for tags_filling_values_tmp in tags_filling.values():
                if isinstance(tags_filling_values_tmp, list):
                    dim_tmp = tags_filling_values_tmp.__len__()
                    if dim_tmp > dim_max:
                        dim_max = dim_tmp

            string_filled_list = [string_filled] * dim_max

            string_filled_def = []
            for string_id, string_filled_step in enumerate(string_filled_list):

                for tag_dict_template, tag_dict_fields in tag_dictionary.items():
                    tag_dict_key = tag_dict_fields['key']
                    tag_dict_value = tag_dict_fields['value']

                    if tag_dict_template in string_filled_step:
                        if tag_dict_value is not None:

                            if tag_dict_key in list(tags_filling.keys()):

                                value_filling_obj = tags_filling[tag_dict_key]

                                if isinstance(value_filling_obj, list):
                                    value_filling = value_filling_obj[string_id]
                                else:
                                    value_filling = value_filling_obj

                                string_filled_step = string_filled_step.replace(tag_dict_template, tag_dict_key)

                                if isinstance(value_filling, datetime):
                                    tag_dict_value = value_filling.strftime(tag_dict_value)
                                elif isinstance(value_filling, (float, int)):
                                    tag_dict_value = tag_dict_key.format(value_filling)
                                else:
                                    tag_dict_value = value_filling

                                string_filled_step = string_filled_step.replace(tag_dict_key, tag_dict_value)

                string_filled_def.append(string_filled_step)

            if dim_max == 1:
                string_filled_out = string_filled_def[0].replace('//', '/')
            else:
                string_filled_out = []
                for string_filled_tmp in string_filled_def:
                    string_filled_out.append(string_filled_tmp.replace('//', '/'))

            return string_filled_out
        else:
            return string_raw
    else:
        return None
# -------------------------------------------------------------------------------------
