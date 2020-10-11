"""
Library Features:

Name:          lib_utils_dict
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging

import functools
import numpy as np

from collections import MutableMapping
from operator import getitem

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to get all dictionary item(s)
def get_dict_all_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield from get_dict_all_items(value)
        else:
            yield (key, value)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to delete dict keys
def delete_dict_keys(dictionary, keys):
    keys_set = set(keys)  # Just an optimization for the "if key in keys" lookup.

    modified_dict = {}
    for key, value in dictionary.items():
        if key not in keys_set:
            if isinstance(value, MutableMapping):
                modified_dict[key] = delete_dict_keys(value, keys_set)
            else:
                modified_dict[key] = value  # or copy.deepcopy(value) if a copy is desired for non-dicts.
    return modified_dict
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get nested value
def get_dict_nested_value(input_dict, nested_key):
    internal_dict_value = input_dict
    for k in nested_key:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to build dict tree
def build_dict_tree(tree_list):
    if tree_list:
        return {tree_list[0]: build_dict_tree(tree_list[1:])}
    return {}
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get value from dictionary (using a list)
def lookup_dict_keys(dataDict, mapList):
    return functools.reduce(lambda d, k: d[k], mapList, dataDict)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to set dictionary values
def set_dict_values(dataDict, mapList, val):
    """Set item in nested dictionary"""
    functools.reduce(getitem, mapList[:-1], dataDict)[mapList[-1]] = val
    return dataDict
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get recursively dictionary value
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

                    if not isinstance(vf_end, bool):
                        if vf_end:
                            if isinstance(value, list):
                                value.append(vf_end)
                            elif isinstance(value, str):
                                value = [value, vf_end]
                        else:
                            pass
                    else:
                        value.append(vf_end)
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
