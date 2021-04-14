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
                 flag_terrain_data='Terrain', flag_grid_data='Grid',
                 flag_static_source='source', flag_static_destination='destination',
                 flag_cleaning_static=True):

        self.flag_terrain_data = flag_terrain_data
        self.flag_grid_data = flag_grid_data

        self.flag_static_source = flag_static_source
        self.flag_static_destination = flag_static_destination

        self.alg_ancillary = alg_ancillary

        self.alg_template_tags = alg_template_tags
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.folder_name_terrain_src = src_dict[self.flag_terrain_data][self.folder_name_tag]
        self.file_name_terrain_src = src_dict[self.flag_terrain_data][self.file_name_tag]
        self.file_path_terrain_src = os.path.join(self.folder_name_terrain_src, self.file_name_terrain_src)

        self.grid_info_src = src_dict[self.flag_grid_data]

        self.folder_name_terrain_dst = dst_dict[self.flag_terrain_data][self.folder_name_tag]
        self.file_name_terrain_dst = dst_dict[self.flag_terrain_data][self.file_name_tag]
        self.file_path_terrain_dst = os.path.join(self.folder_name_terrain_dst, self.file_name_terrain_dst)

        self.grid_info_dst = dst_dict[self.flag_grid_data]

        self.flag_cleaning_static = flag_cleaning_static

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_static(self):

        # Info start
        log_stream.info(' ---> Organize static datasets ... ')

        # Data collection object
        data_collections = {self.flag_static_source: {}, self.flag_static_destination: {}}

        # Read static data source
        terrain_data_src = read_data_grid(self.file_path_terrain_src, output_format='dictionary')
        terrain_grid_src = extract_data_grid(terrain_data_src['values'],
                                             terrain_data_src['longitude'], terrain_data_src['latitude'],
                                             terrain_data_src['transform'])
        data_collections[self.flag_static_source][self.flag_terrain_data] = terrain_grid_src

        generic_grid_src = create_data_grid(self.grid_info_src)
        data_collections[self.flag_static_source][self.flag_grid_data] = generic_grid_src

        # Read static data destination
        terrain_data_dst = read_data_grid(self.file_path_terrain_dst, output_format='dictionary')
        terrain_grid_dst = extract_data_grid(terrain_data_dst['values'],
                                             terrain_data_dst['longitude'], terrain_data_dst['latitude'],
                                             terrain_data_dst['transform'])
        data_collections[self.flag_static_destination][self.flag_terrain_data] = terrain_grid_dst

        generic_grid_dst = create_data_grid(self.grid_info_dst)
        data_collections[self.flag_static_destination][self.flag_grid_data] = generic_grid_dst

        # Info end
        log_stream.info(' ---> Organize static datasets ... DONE')

        return data_collections
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
