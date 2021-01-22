"""
Library Features:

Name:          lib_utils_list
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging

from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to pad or truncate list
def pad_or_truncate_list(some_list, target_len, fill_value=-9999.0):
    return some_list[:target_len] + [fill_value]*(target_len - len(some_list))
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to flat list of list
def flat_list(lists):
    return [item for sublist in lists for item in sublist]
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert coupled list to dictionary
def merge_lists_4_dict(list_keys, list_values):
    dictionary = {k: v for k, v in zip(list_keys, list_values)}
    return dictionary
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert list 2 dictionary
def convert_list_2_dict(var_list):
    var_dict = {}
    for step, var in enumerate(var_list):
        var_dict[step] = var
    return var_dict
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert list to string (given an delimiter)
def convert_list_2_string(list_data, list_delimiter=','):
    string_data = list_delimiter.join(str(elem) for elem in list_data)
    return string_data
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert string to list (given an delimiter)
def convert_string_2_list(str_data, str_delimiter=' '):
    list_data = str_data.split(str_delimiter)
    return list_data
# -------------------------------------------------------------------------------------
