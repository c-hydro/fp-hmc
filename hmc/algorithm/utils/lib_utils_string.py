"""
Library Features:

Name:          lib_utils_string
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200402'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import re

from datetime import datetime
from copy import deepcopy

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to convert bytes string to character string
def separate_number_chars(s):
    res = re.split('([-+]?\d+\.\d+)|([-+]?\d+)', s.strip())
    res_f = [r.strip() for r in res if r is not None and r.strip() != '']
    return res_f
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert bytes string to character string
def convert_bytes2string(obj_bytes):
    if isinstance(obj_bytes, bytes):
        obj_string = obj_bytes.decode()
        obj_string = obj_string.rstrip("\n")
    else:
        obj_string = obj_bytes
    return obj_string
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to remove string part(s)
def remove_string_parts(string_raw, deny_parts_list=None):
    if deny_parts_list is not None:
        for deny_part in deny_parts_list:
            if deny_part in string_raw:
                string_raw = string_raw.replace(deny_part, '')
        string_raw = string_raw.replace('{}', '')
        string_raw = string_raw.replace('//', '/')
    return string_raw
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to parse complex row to string
def parse_row2string(row_obj, row_delimiter='#'):

    row_string = row_obj.split(row_delimiter)[0]

    # Check delimiter character (in intake file info there are both '#' and '%')
    if ('#' not in row_obj) and ('%' in row_string):
        row_string = row_obj.split('%')[0]

    row_string = row_string.strip()

    return row_string
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to add time in a unfilled string (path or filename)
def fill_tags2string(string_raw, tags_format=None, tags_filling=None):

    apply_tags = False
    if string_raw is not None:
        for tag in list(tags_format.keys()):
            if tag in string_raw:
                apply_tags = True
                break

    if apply_tags:

        tags_format_tmp = deepcopy(tags_format)
        for tag_key, tag_value in tags_format.items():
            tag_key_tmp = '{' + tag_key + '}'
            if tag_value is not None:
                if tag_key_tmp in string_raw:
                    string_filled = string_raw.replace(tag_key_tmp, tag_value)
                    string_raw = string_filled
                else:
                    tags_format_tmp.pop(tag_key, None)

        dim_max = 1
        for tags_filling_values_tmp in tags_filling.values():
            if isinstance(tags_filling_values_tmp, list):
                dim_tmp = tags_filling_values_tmp.__len__()
                if dim_tmp > dim_max:
                    dim_max = dim_tmp

        string_filled_list = [string_filled] * dim_max

        string_filled_def = []
        for string_id, string_filled_step in enumerate(string_filled_list):
            for tag_format_name, tag_format_value in list(tags_format_tmp.items()):

                if tag_format_name in list(tags_filling.keys()):
                    tag_filling_value = tags_filling[tag_format_name]

                    if isinstance(tag_filling_value, list):
                        tag_filling_step = tag_filling_value[string_id]
                    else:
                        tag_filling_step = tag_filling_value

                    if tag_filling_step is not None:

                        if isinstance(tag_filling_step, datetime):
                            tag_filling_step = tag_filling_step.strftime(tag_format_value)

                        if isinstance(tag_filling_step, (float, int)):
                            tag_filling_step = tag_format_value.format(tag_filling_step)

                        string_filled_step = string_filled_step.replace(tag_format_value, tag_filling_step)

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
# -------------------------------------------------------------------------------------

