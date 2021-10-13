"""
Class Features

Name:          driver_data_io_geo
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os

from tools.preprocessing_tool_source2nc_converter.lib_data_io_ascii import read_data_grid, \
    create_data_grid, extract_data_grid
from tools.preprocessing_tool_source2nc_converter.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

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
                 flag_file_data='file_obj', flag_grid_data='grid_obj',
                 flag_static_source='source', flag_static_destination='destination',
                 flag_cleaning_static=True):

        self.flag_file_data = flag_file_data
        self.flag_grid_data = flag_grid_data

        self.flag_static_source = flag_static_source
        self.flag_static_destination = flag_static_destination

        self.alg_ancillary = alg_ancillary

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.file_obj_fields = [self.file_name_tag, self.folder_name_tag]
        self.grid_obj_fields = ["xll", "yll", "res", "nrows", "ncols"]

        self.obj_static_src = {}
        for src_key, src_fields in src_dict.items():

            if all(key in list(src_fields.keys()) for key in self.file_obj_fields):
                folder_name_src = src_fields[self.folder_name_tag]
                file_name_src = src_fields[self.file_name_tag]
                file_path_src = os.path.join(folder_name_src, file_name_src)
                self.obj_static_src[src_key] = {}
                self.obj_static_src[src_key]['fields'] = file_path_src
                self.obj_static_src[src_key]['type'] = self.flag_file_data
            elif all(key in list(src_fields.keys()) for key in self.grid_obj_fields):
                self.obj_static_src[src_key] = {}
                self.obj_static_src[src_key]['fields'] = src_fields
                self.obj_static_src[src_key]['type'] = self.flag_grid_data
            else:
                log_stream.error(' ===> Static source key "' + src_key + '" is not in allowed format')
                raise NotImplementedError('Case not implemented yet')

        self.obj_static_dst = {}
        for dst_key, dst_fields in dst_dict.items():

            if all(key in list(dst_fields.keys()) for key in self.file_obj_fields):
                folder_name_src = dst_fields[self.folder_name_tag]
                file_name_src = dst_fields[self.file_name_tag]
                file_path_src = os.path.join(folder_name_src, file_name_src)
                self.obj_static_dst[dst_key] = {}
                self.obj_static_dst[dst_key]['fields'] = file_path_src
                self.obj_static_dst[dst_key]['type'] = self.flag_file_data
            elif all(key in list(dst_fields.keys()) for key in self.grid_obj_fields):
                self.obj_static_dst[dst_key] = {}
                self.obj_static_dst[dst_key]['fields'] = dst_fields
                self.obj_static_dst[dst_key]['type'] = self.flag_grid_data
            else:
                log_stream.error(' ===> Static destination key "' + dst_key + '" is not in allowed format')
                raise NotImplementedError('Case not implemented yet')

        self.flag_cleaning_static = flag_cleaning_static

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_static(self):

        # Info start
        log_stream.info(' ---> Organize static datasets ... ')

        # Get static objects
        obj_static_src = self.obj_static_src
        obj_static_dst = self.obj_static_dst

        # Data collection object
        data_collections = {self.flag_static_source: {}, self.flag_static_destination: {}}

        # Read static data source
        for obj_key, obj_collections in obj_static_src.items():
            obj_data_grid = None
            if obj_collections['type'] == self.flag_file_data:
                obj_data_file = obj_collections['fields']
                obj_data_tmp = read_data_grid(obj_data_file, output_format='dictionary')
                obj_data_grid = extract_data_grid(obj_data_tmp['values'],
                                                  obj_data_tmp['longitude'], obj_data_tmp['latitude'],
                                                  obj_data_tmp['transform'], obj_data_tmp['bbox'])
            elif obj_collections['type'] == self.flag_grid_data:
                obj_data_fields = obj_collections['fields']
                obj_data_grid = create_data_grid(obj_data_fields)

            data_collections[self.flag_static_source][obj_key] = obj_data_grid

        # Read static data destination
        for obj_key, obj_collections in obj_static_dst.items():
            obj_data_grid = None
            if obj_collections['type'] == self.flag_file_data:
                obj_data_file = obj_collections['fields']
                obj_data_tmp = read_data_grid(obj_data_file, output_format='dictionary')
                obj_data_grid = extract_data_grid(obj_data_tmp['values'],
                                                  obj_data_tmp['longitude'], obj_data_tmp['latitude'],
                                                  obj_data_tmp['transform'], obj_data_tmp['bbox'])
            elif obj_collections['type'] == self.flag_grid_data:
                obj_data_fields = obj_collections['fields']
                obj_data_grid = create_data_grid(obj_data_fields)

            data_collections[self.flag_static_destination][obj_key] = obj_data_grid

        # Info end
        log_stream.info(' ---> Organize static datasets ... DONE')

        return data_collections
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
