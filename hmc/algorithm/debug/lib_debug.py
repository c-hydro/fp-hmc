"""
Library Features:

Name:          lib_debug
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""
#######################################################################################
# Library
import logging
import os
import shelve
import pickle
import scipy.io as sio

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to read workspace obj
def read_workspace_obj(file_name):
    if os.path.exists(file_name):
        file_data = pickle.load(open(file_name, "rb"))
    else:
        file_data = None
    return file_data
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write workspace obj
def write_workspace_obj(file_name, file_data):
    if os.path.exists(file_name):
        os.remove(file_name)
    with open(file_name, 'wb') as file_handle:
        pickle.dump(file_data, file_handle, protocol=pickle.HIGHEST_PROTOCOL)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write workspace variable(s)
def write_workspace_vars(file_name, **kwargs):
    # Remove old workspace
    if os.path.exists(file_name):
        os.remove(file_name)
    # Save new workspace
    file_handle = shelve.open(file_name, 'n')
    for key, value in iter(kwargs.items()):
        file_handle[key] = value
    file_handle.close()
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to restore variable(s) workspace
def read_workspace_vars(file_name):
    file_handle = shelve.open(file_name)
    file_dict = {}
    for key in file_handle:
        file_dict[key] = file_handle[key]
    file_handle.close()
    return file_dict
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to write mat file
def write_workspace_mat(file_name, file_data, file_key):
    file_handle = {file_key: file_data}
    sio.savemat(file_name, file_handle)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read mat file
def read_workspace_mat(file_name):
    return sio.loadmat(file_name)
# -------------------------------------------------------------------------------------
