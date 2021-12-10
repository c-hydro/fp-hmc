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

from tools.processing_tool_json2dew_converter.lib_data_io_shapefile import read_data_section, read_data_dam

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
                 flag_point_data='point_data',
                 flag_point_type='point_type', flag_point_variable='point_variable',
                 flag_domain_collections='domain_collection',
                 flag_cleaning_static=True):

        self.flag_point_data = flag_point_data
        self.flag_point_type = flag_point_type
        self.flag_point_variable = flag_point_variable

        self.flag_domain_collections = flag_domain_collections

        self.alg_ancillary = alg_ancillary

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'
        self.data_type_tag = 'type'
        self.data_variable_tag = 'variable'

        self.folder_name_point = src_dict[self.flag_point_data][self.folder_name_tag]
        self.file_name_point = src_dict[self.flag_point_data][self.file_name_tag]
        self.file_path_point = os.path.join(self.folder_name_point, self.file_name_point)

        if self.data_variable_tag in list(src_dict[self.flag_point_data].keys()):
            self.data_variable = src_dict[self.flag_point_data][self.data_variable_tag]
        else:
            self.data_variable = 'discharge'
        if self.data_type_tag in list(src_dict[self.flag_point_data].keys()):
            self.data_type = src_dict[self.flag_point_data][self.data_type_tag]
        else:
            self.data_type = 'section'

        self.flag_cleaning_static = flag_cleaning_static

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_static(self):

        # Info start
        logging.info(' ---> Organize static datasets ... ')

        # Data collection object
        data_collections = {self.flag_point_type: self.data_type, self.flag_point_variable: self.data_variable}

        # Read section shapefile datasets
        if self.data_type == 'section':
            data_point = read_data_section(self.file_path_point)
        elif self.data_type == 'dam':
            data_point = read_data_dam(self.file_path_point)
        else:
            logging.error(' ---> Organize static datasets ... FAILED. Datatype "' +
                          self.data_type + '" not allowed. Accepted datatype: "section", "dam".')
            raise NotImplementedError('Datatype not implemented yet')

        # Collect datasets in a common object
        data_collections[self.flag_point_data] = data_point

        # Info end
        logging.info(' ---> Organize static datasets ... DONE')

        return data_collections
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
