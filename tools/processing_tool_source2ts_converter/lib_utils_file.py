"""
Library Features:

Name:          lib_utils_file
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""
# ----------------------------------------------------------------------------------------------------------------------
# libraries
import logging
import os
from copy import deepcopy

from lib_utils_system import fill_tags2string
from lib_info_args import logger_name, zip_extension

# logging
log_stream = logging.getLogger(logger_name)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to check source format
def check_file_or_grid(obj_data, obj_fields_file=None, obj_fields_coords=None):
    file_flag, coords_flag = False, False

    if obj_fields_coords is None:
        obj_fields_coords = ["xll", "yll", "res", "nrows", "ncols"]
    if obj_fields_file is None:
        obj_fields_file = ['folder_name', 'file_name']

    if all([field in obj_data.keys() for field in obj_fields_file]):
        file_flag = True
    if all([field in obj_data.keys() for field in obj_fields_coords]):
        coords_flag = True

    return file_flag, coords_flag
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to get file field
def get_file_field(obj_data, data_name='folder_name', data_default=None):
    if data_name in obj_data.keys():
        data_value = obj_data[data_name]
    else:
        data_value = deepcopy(data_default)
    return data_value


# method to compose file fields
def define_file_fields(obj_data, obj_fields_list=None, obj_fields_default=None):

    if obj_fields_list is None:
        obj_fields_list = ['folder_name', 'file_name', 'file_path']
    if obj_fields_default is None:
        obj_fields_default = [None] * obj_fields_list.__len__()

    obj_fields = {}
    for field_name, field_default in zip(obj_fields_list, obj_fields_default):
        field_value = get_file_field(obj_data, data_name=field_name, data_default=field_default)
        obj_fields[field_name] = field_value

    if ('file_path' not in obj_fields.keys()) or (obj_fields['file_path'] is None):
        file_path = None
        if 'folder_name' in obj_fields.keys() and 'file_name' in obj_fields.keys():
            folder_name, file_name = obj_fields['folder_name'], obj_fields['file_name']
            if folder_name is not None and file_name is not None:
                file_path = os.path.join(folder_name, file_name)
        obj_fields['file_path'] = file_path

    return obj_fields
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to compose file name
def define_file_name(file_name_raw, file_template_keys=None, file_template_values=None):
    if (file_template_keys is None) or (file_template_values is None):
        log_stream.warning(' ===> File name template keys or values are not defined')
        file_name_def = None
    else:
        file_name_def = fill_tags2string(file_name_raw, tags_format=file_template_keys, tags_filling=file_template_values)
    return file_name_def
# ----------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to define unzipped filename(s)
def define_file_unzip(file_path_zip, file_extension_zip=None):

    if file_extension_zip is None:
        file_extension_zip = zip_extension

    if file_path_zip.endswith(file_extension_zip):
        file_path_tmp, file_extension_tmp = os.path.splitext(file_path_zip)

        if file_extension_tmp.replace('.', '') == file_extension_zip.replace('.', ''):
            file_path_unzip = file_path_tmp
        else:
            log_stream.error(' ===> File zip extension was not expected in format "' + file_extension_tmp
                             + '"; expected format was "' + file_extension_zip + '"')
            raise IOError('Check your settings file or change expected zip extension')
    else:
        log_stream.error(' ===> File zip ended with a unexpected zip extension "' + file_extension_tmp
                         + '"; expected format was "' + file_extension_zip + '"')
        raise IOError('Check your settings file or change expected zip extension')

    return file_path_unzip
# -------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# method to define
def define_file_zip(file_path_unzip, file_extension_zip=None):

    if file_extension_zip is None:
        file_extension_zip = zip_extension

    file_extension_zip = file_extension_zip.replace('.', '')

    file_path_zip = deepcopy(file_path_unzip)
    if not file_path_unzip.endswith(file_extension_zip):
        file_path_zip = '.'.join([file_path_unzip, file_extension_zip])
    elif file_path_unzip.endswith(file_extension_zip):
        file_path_zip = deepcopy(file_path_unzip)

    return file_path_zip
# ----------------------------------------------------------------------------------------------------------------------
