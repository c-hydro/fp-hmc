"""
Library Features:

Name:          lib_utils_system
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os
import shutil

from os.path import exists

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to split full path in root and filename
def split_path(file_path):
    file_root, file_name = os.path.split(file_path)
    return file_root, file_name
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to create folder (and check if folder exists)
def create_folder(path_name=None, path_delimiter=None):
    if path_name:
        if path_delimiter:
            path_name_tmp = path_name.split(path_delimiter)[0]
        else:
            path_name_tmp = path_name
        if not exists(path_name_tmp):
            os.makedirs(path_name_tmp)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to delete folder (and check if folder exists)
def delete_folder(path_name):
    # Check folder status
    if os.path.exists(path_name):
        # Remove folder (file only-read too)
        shutil.rmtree(path_name, ignore_errors=True)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to delete file
def delete_file(file_path, file_delete=True):
    if file_delete:
        if os.path.isfile(file_path):
            os.remove(file_path)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to copy file from source to destination
def copy_file(file_path_src, file_path_dest):
    if os.path.exists(file_path_src):
        if not file_path_src == file_path_dest:
            if os.path.exists(file_path_dest):
                os.remove(file_path_dest)
            shutil.copy2(file_path_src, file_path_dest)
    else:
        log_stream.warning(' ===> Copy file failed! Source not available!')
# -------------------------------------------------------------------------------------
