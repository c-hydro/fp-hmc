"""
Class Features

Name:          driver_data_io_static
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20240222'
Version:       '1.0.0'
"""

# ----------------------------------------------------------------------------------------------------------------------
# libraries
import logging
import os

from lib_utils_file import check_file_or_grid, define_file_fields, define_file_name
from lib_utils_io import write_obj
from lib_data_io_shapefile import read_data_point, select_data_point
from lib_data_io_ascii import read_data_grid
from lib_info_args import logger_name

# logging
log_stream = logging.getLogger(logger_name)

# debugging
# import matplotlib.pylab as plt
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# class driver static
class DriverStatic:

    # ------------------------------------------------------------------------------------------------------------------
    # class initialization
    def __init__(self, src_dict, dst_dict=None,
                 info_dict=None, template_dict=None,
                 reset_data=True):

        self.src_obj_grid = src_dict['grid']
        self.src_obj_point = src_dict['point']
        self.dst_obj = dst_dict

        self.info_obj_domain = info_dict['domain_name']
        self.info_obj_analysis = info_dict['analysis']

        self.template_obj_time = template_dict['time']
        self.template_obj_info = template_dict['info']

        self.reset_data = reset_data

        self.tag_file_name, self.tag_folder_name = 'file_name', 'folder_name'
        self.tag_file_compression, self.tag_file_type = 'file_compression', 'file_type'
        self.tag_file_fields = 'file_fields'

        self.obj_fields_file = [self.tag_folder_name, self.tag_file_name]
        self.obj_fields_coords = ["xll", "yll", "res", "nrows", "ncols"]

        self.obj_fields_data_name = [
            self.tag_file_name, self.tag_folder_name, self.tag_file_compression,
            self.tag_file_type, self.tag_file_fields]
        self.obj_fields_data_default = [
            None, None, False,
            'ascii', None]

        self.flag_file, self.flag_coords = check_file_or_grid(
            self.src_obj_grid,
            obj_fields_file=self.obj_fields_file, obj_fields_coords=self.obj_fields_coords)
        self.src_fields_grid = define_file_fields(
            self.src_obj_grid,
            obj_fields_list=self.obj_fields_data_name, obj_fields_default=self.obj_fields_data_default)
        self.dst_fields_grid = define_file_fields(
            self.dst_obj,
            obj_fields_list=self.obj_fields_data_name, obj_fields_default=self.obj_fields_data_default)

        self.fields_point = define_file_fields(
            self.src_obj_point,
            obj_fields_list=self.obj_fields_data_name, obj_fields_default=self.obj_fields_data_default)

    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to get datasets point
    def get_datasets_point(self, point_fields):

        # check file path
        if 'file_path' in point_fields.keys():

            # get file path
            file_path_src_raw = point_fields['file_path']

            # iterate over domain(s)
            fields_point = {}
            for domain_name in self.info_obj_domain:

                # compose file name(s)
                file_path_src_filled = define_file_name(
                    file_path_src_raw,
                    file_template_keys=self.template_obj_info, file_template_values={'domain_name': domain_name})

                # check file path
                if os.path.exists(file_path_src_filled):
                    # get data point
                    dset_point_raw = read_data_point(
                        file_path_src_filled,
                        columns_name_expected_in=list(self.fields_point['file_fields']['lut'].values()),
                        columns_name_expected_out=list(self.fields_point['file_fields']['lut'].keys()),
                        columns_name_type=list(self.fields_point['file_fields']['type'].values()))
                else:
                    log_stream.error(' ===> File point "' + file_path_src_filled + '" is not found')
                    raise IOError('File path "' + file_path_src_filled + '" must be defined')

                # select domain data point(s)
                dset_point_select = select_data_point(dset_point_raw, tag_name='domain', tag_value=domain_name)
                # check domain data point(s)
                if dset_point_select is None or dset_point_select.empty:
                    log_stream.warning(' ===> Domain "' + domain_name +
                                       '" is not found in point dataset. Point dataset is null')

                # store data in a dictionary
                fields_point[domain_name] = dset_point_select

            return fields_point

        else:
            log_stream.error(' ===> Datasets point variable "file_path" is not defined')
            raise RuntimeError('Variable "file_path" must be defined by "folder_name" and "file_name" tags')

    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to get datasets grid
    def get_datasets_grid(self, src_fields_grid, dst_fields_grid):

        # check file path
        if ('file_path' in src_fields_grid.keys()) and ('file_path' in dst_fields_grid.keys()):

            # get file path(s)
            file_path_src, file_path_dst = src_fields_grid['file_path'], dst_fields_grid['file_path']

            # iterate over domain(s)
            fields_grid = {}
            for domain_name in self.info_obj_domain:

                # compose file name(s)
                file_path_src_filled = define_file_name(
                    file_path_src,
                    file_template_keys=self.template_obj_info, file_template_values={'domain_name': domain_name})
                file_path_dst_filled = define_file_name(
                    file_path_dst,
                    file_template_keys=self.template_obj_info, file_template_values={'domain_name': domain_name})

                # reset data grid
                if self.reset_data:
                    if os.path.exists(file_path_dst_filled):
                        os.remove(file_path_dst_filled)

                # check file path(s)
                if (os.path.exists(file_path_src_filled)) and (not os.path.exists(file_path_dst_filled)):

                    # get data grid
                    dset_src = read_data_grid(file_path_src_filled, output_format='dictionary')

                    # save data
                    folder_name_dst, file_name_dst = os.path.split(file_path_dst_filled)
                    os.makedirs(folder_name_dst, exist_ok=True)
                    write_obj(file_path_dst_filled, dset_src)

                    # store filename(s)
                    fields_grid[domain_name] = file_path_dst_filled

                else:
                    log_stream.warning(' ===> File grid "' + file_path_src_filled + '" is not found')

            return fields_grid

        else:
            log_stream.error(' ===> Datasets grid variable "file_path" is not defined')
            raise RuntimeError('Variable "file_path" must be defined by "folder_name" and "file_name" tags')
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to organize datasets
    def organize_datasets(self):

        # info method start
        log_stream.info(' ---> Organize static datasets ... ')

        # get objects
        src_fields_grid, dst_fields_grid = self.src_fields_grid, self.dst_fields_grid
        fields_point = self.fields_point

        # get point datasets
        datasets_point = self.get_datasets_point(fields_point)
        # get datasets grid
        datasets_grid = self.get_datasets_grid(src_fields_grid, dst_fields_grid)

        # creata datasets collection
        datasets_collections = {'point': datasets_point, 'grid': datasets_grid}

        # info method start
        log_stream.info(' ---> Organize static datasets ... DONE')

        return datasets_collections
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
