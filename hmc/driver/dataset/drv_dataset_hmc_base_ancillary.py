"""
Class Features

Name:          drv_configuration_hmc_ancillary
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging
import os

from hmc.algorithm.utils.lib_utils_system import create_folder
from hmc.algorithm.utils.lib_utils_string import fill_tags2string
from hmc.algorithm.utils.lib_utils_dict import get_dict_all_items
from hmc.algorithm.utils.lib_utils_string import remove_string_parts

from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to configure ancillary
class ModelAncillary:

    # -------------------------------------------------------------------------------------
    # Method class initialization
    def __init__(self, datasets_obj,
                 tag_dset_ancillary='DataAncillary',
                 template_time=None,
                 template_run_ref=None,
                 template_run_def=None,
                 template_static=None, template_dynamic=None, **kwargs):

        self.dset_obj = datasets_obj
        self.dset_ancillary = self.dset_obj[tag_dset_ancillary]

        self.obj_template_time = template_time
        self.obj_template_run_def = template_run_def
        self.obj_template_run_ref = template_run_ref
        self.obj_template_dset_static_ref = template_static
        self.obj_template_dset_dynamic_ref = template_dynamic

        self.file_name_tag = 'hmc_file_name'
        self.folder_name_tag = 'hmc_file_folder'

        self.time_run_tag = 'time_run'

        self.tag_template_excluded = ['run_mode', 'run_var']

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to select template item(s)
    def select_items(self, obj_items_all):

        obj_items_generator = get_dict_all_items(obj_items_all)

        obj_items_reduced = {}
        for obj_items_step in obj_items_generator:

            obj_key = obj_items_step[0]
            obj_value = obj_items_step[1]

            if obj_key not in self.tag_template_excluded:
                if obj_key not in list(obj_items_reduced.keys()):
                    obj_items_reduced[obj_key] = obj_value

        return obj_items_reduced

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize data ancillary
    def organize_data_ancillary(self, time_collections_obj):

        # Starting information
        log_stream.info(' ----> Organize ancillary datasets ... ')

        time_collection_select = self.select_items(time_collections_obj)

        template_time_ref = self.obj_template_time
        template_run_ref = self.obj_template_run_ref
        template_run_def = self.select_items(self.obj_template_run_def)

        ancillary_collections = {}
        for dset_key, dset_data in self.dset_ancillary.items():

            folder_name_tmp = dset_data[self.folder_name_tag]
            file_name_tmp = dset_data[self.file_name_tag]

            folder_name_raw = remove_string_parts(folder_name_tmp, self.tag_template_excluded)
            file_name_raw = remove_string_parts(file_name_tmp, self.tag_template_excluded)

            template_time_def = dict.fromkeys(list(template_time_ref.keys()), time_collection_select[self.time_run_tag])
            template_merge_filled = {**template_run_def, **template_time_def}
            template_merge_ref = {**template_run_ref, **template_time_ref}

            folder_name_def = fill_tags2string(folder_name_raw, template_merge_ref, template_merge_filled)
            file_name_def = fill_tags2string(file_name_raw, template_merge_ref, template_merge_filled)

            create_folder(folder_name_def)
            file_path_def = os.path.join(folder_name_def, file_name_def)

            ancillary_collections[dset_key] = file_path_def

        # Ending information
        log_stream.info(' ----> Organize ancillary datasets ... DONE')

        return ancillary_collections

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
