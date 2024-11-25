"""
Class Features

Name:          driver_data_io_geo
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20240215'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os

from lib_data_io_shapefile import read_data_section, read_data_dam

# Debug
# import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverStatic
class DriverStatic:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, src_dict, dst_dict=None,
                 alg_ancillary=None, alg_template_tags=None):

        # main key(s) information
        self.tag_point_data = 'point_data'
        # sub key(s) information
        self.tag_point_type = 'point_type'
        self.tag_point_variable = 'point_variable'

        self.alg_ancillary = alg_ancillary

        self.alg_template_tags = alg_template_tags
        self.tag_file_name, self.tag_folder_name = 'file_name', 'folder_name'
        self.tag_data_type, self.tag_data_variable = 'type', 'variable'
        self.tag_data_fields_name = 'fields_name'
        self.tag_data_fields_type = 'fields_type'
        self.tag_data_fields_key = 'fields_key'

        self.folder_name_point = src_dict[self.tag_point_data][self.tag_folder_name]
        self.file_name_point = src_dict[self.tag_point_data][self.tag_file_name]
        self.file_path_point = os.path.join(self.folder_name_point, self.file_name_point)

        self.data_variable = src_dict[self.tag_point_data][self.tag_data_variable]
        self.data_type = src_dict[self.tag_point_data][self.tag_data_type]
        self.data_fields_name = src_dict[self.tag_point_data][self.tag_data_fields_name]
        self.data_fields_type = src_dict[self.tag_point_data][self.tag_data_fields_type]
        self.data_fields_key = src_dict[self.tag_point_data][self.tag_data_fields_key]

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_static(self):

        # Info start
        logging.info(' ---> Organize static datasets ... ')

        # Data collection object
        data_collections = {self.tag_point_type: self.data_type, self.tag_point_variable: self.data_variable}

        # check file point availability
        if not os.path.exists(self.file_path_point):
            logging.error(' ---> Organize static datasets ... FAILED. File "' +
                          self.file_path_point + '" not found.')
            raise IOError('File not found. Check your path or filename.')

        # Read section shapefile datasets
        if self.data_type == 'section':
            data_point = read_data_section(
                self.file_path_point,
                columns_name_expected_in=self.data_fields_name,
                columns_name_expected_out=self.data_fields_key,
                columns_name_type=self.data_fields_type)
        elif self.data_type == 'dam':
            # data_point = read_data_dam(self.file_path_point)
            logging.error(' ---> Organize static datasets ... FAILED. Datatype "' +
                          self.data_type + '" not allowed. Type "dam" not implemented yet.')
            raise NotImplemented('Datatype not implemented yet')
        else:
            logging.error(' ---> Organize static datasets ... FAILED. Datatype "' +
                          self.data_type + '" not allowed. Accepted datatype: "section", "dam".')
            raise NotImplementedError('Datatype not expected. Check your datatype.')

        # Collect datasets in a common object
        data_collections[self.tag_point_data] = data_point

        # Info end
        logging.info(' ---> Organize static datasets ... DONE')

        return data_collections
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
