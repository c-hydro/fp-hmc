"""
Class Features

Name:          drv_configuration_hmc_logging
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os

from hmc.algorithm.io.lib_data_io_json import read_file_json
from hmc.algorithm.log.lib_logging import set_logging_stream

from hmc.algorithm.utils.lib_utils_dict import get_dict_nested_value
from hmc.algorithm.utils.lib_utils_string import fill_tags2string
from hmc.algorithm.utils.lib_utils_system import create_folder

from hmc.algorithm.default.lib_default_args import logger_name, logger_file, logger_handle, logger_format

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class Tags
class ModelLogging:

    # -------------------------------------------------------------------------------------
    # Method class initialization
    def __init__(self, file_algorithm, tag_logging_file=None, tag_run_name=None, tag_run_domain=None,
                 tag_template_logging=None):

        # -------------------------------------------------------------------------------------
        # Store information in global workspace
        self.file_algorithm = file_algorithm
        self.file_handle = read_file_json(file_algorithm)

        if tag_logging_file is None:
            tag_logging_file = ['Run_Info', 'run_location', 'log']
        if tag_run_name is None:
            tag_run_name = ['Run_Info', 'run_type', 'run_name']
        if tag_run_domain is None:
            tag_run_domain = ['Run_Info', 'run_type', 'run_domain']
        if tag_template_logging is None:
            tag_template_logging = ['Template', 'run']

        self.file_log = get_dict_nested_value(self.file_handle, tag_logging_file)
        self.run_name = get_dict_nested_value(self.file_handle, tag_run_name)
        self.run_domain = get_dict_nested_value(self.file_handle, tag_run_domain)

        self.template_logging_ref = get_dict_nested_value(self.file_handle, tag_template_logging)
        self.template_logging_def = {'run_domain': self.run_domain, 'run_name': self.run_name}
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set data tags
    def configure_logging(self, tag_filename='file_name', tag_folder='file_folder'):

        file_name_raw = self.file_log[tag_filename]
        folder_name_raw = self.file_log[tag_folder]
        file_name_def = fill_tags2string(file_name_raw, self.template_logging_ref, self.template_logging_def)
        folder_name_def = fill_tags2string(folder_name_raw, self.template_logging_ref, self.template_logging_def)

        create_folder(folder_name_def)
        file_logging = os.path.join(folder_name_def, file_name_def)

        if file_logging is None:
            file_logging = logger_file

        log_stream = set_logging_stream(file_logging, logger_name, logger_handle, logger_format)

        return log_stream
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
