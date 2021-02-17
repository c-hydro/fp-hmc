"""
Class Features

Name:          driver_data_io_geo
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200515'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os

from tools.postprocessing_tool_ensemble_maker.lib_data_io_shapefile import read_data_section

# Debug
# import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverStatic
class DriverStatic:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, src_dict, dst_dict=None,
                 alg_ancillary=None, alg_template_tags=None,
                 flag_section_data='section_data',
                 flag_domain_collections='domain_collection',
                 flag_cleaning_static=True):

        self.flag_section_data = flag_section_data
        self.flag_domain_collections = flag_domain_collections

        self.alg_ancillary = alg_ancillary

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.folder_name_section = src_dict[self.flag_section_data][self.folder_name_tag]
        self.file_name_section = src_dict[self.flag_section_data][self.file_name_tag]
        self.file_path_section = os.path.join(self.folder_name_section, self.file_name_section)

        self.flag_cleaning_static = flag_cleaning_static

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_static(self):

        # Info start
        logging.info(' ---> Organize static datasets ... ')

        # Data collection object
        data_collections = {}

        # Read section shapefile datasets
        data_section = read_data_section(self.file_path_section)

        # Collect datasets in a common object
        data_collections[self.flag_section_data] = data_section

        # Info end
        logging.info(' ---> Organize static datasets ... DONE')

        return data_collections
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
