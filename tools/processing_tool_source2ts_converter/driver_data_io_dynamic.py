"""
Class Features

Name:          driver_data_io_dynamic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""

# ----------------------------------------------------------------------------------------------------------------------
# libraries
import logging
import os
import pandas as pd

from copy import deepcopy

from lib_utils_file import define_file_fields, define_file_name, define_file_unzip
from lib_data_io_generic import extract_data_point, combine_data_point
from lib_data_io_binary import read_data_binary
from lib_data_io_tiff import read_data_tiff
from lib_data_io_nc import read_data_nc
from lib_data_io_csv import write_file_csv

from lib_utils_io import read_obj, write_obj
from lib_utils_gzip import unzip_filename
from lib_info_args import logger_name, time_format_algorithm
from lib_info_args import time_var_name, time_coord_name, time_dim_name
from lib_info_args import (geo_var_name_x, geo_var_name_y,
                           geo_coord_name_x, geo_coord_name_y, geo_dim_name_x, geo_dim_name_y)

# logging
log_stream = logging.getLogger(logger_name)

# debugging
import matplotlib.pylab as plt
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# algorithm default definition(s)
tag_var_compute, tag_var_name, tag_var_sf, tag_format_var = 'var_compute', 'var_name', 'var_scale_factor', 'var_format'
tag_file_name, tag_folder_name = 'file_name', 'folder_name'
tag_file_compression, tag_file_geo_reference = 'file_compression', 'file_geo_reference'
tag_file_type, tag_file_frequency = 'file_type', 'file_frequency'
tag_file_coords, tag_file_fields = 'file_coords', 'file_fields'
tag_file_no_data, tag_file_delimiter = 'file_no_data', 'file_delimiter'
tag_file_decimal_precision, tag_file_date_format = 'file_decimal_precision', 'file_date_format'
tag_file_date_order = 'file_date_order'
# -----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Class DriverDynamic
class DriverDynamic:

    # ------------------------------------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self,
                 time_run, time_step,
                 src_dict, anc_dict=None, dst_dict=None,
                 geo_dict=None,
                 info_dict=None, template_dict=None,
                 reset_dynamic_data=True, reset_dynamic_tmp=True):

        self.time_run = time_run
        self.time_step = time_step

        self.src_obj = src_dict
        if '__comment__' in list(self.src_obj.keys()):
            self.src_obj.pop('__comment__')
        self.anc_obj = anc_dict
        self.dst_obj = dst_dict
        if '__comment__' in list(self.dst_obj.keys()):
            self.dst_obj.pop('__comment__')

        self.info_obj_domain = info_dict['domain_name']
        self.info_obj_analysis = info_dict['analysis']
        self.info_obj_variable = list(self.src_obj.keys())

        self.template_obj_time = template_dict['time']
        self.template_obj_info = template_dict['info']

        self.geo_obj = geo_dict

        self.reset_dynamic_data = reset_dynamic_data
        self.reset_dynamic_tmp = reset_dynamic_tmp

        self.geo_collections_grid = self.set_reference_geo(self.geo_obj, 'grid')
        self.geo_collections_point = self.set_reference_geo(self.geo_obj, 'point')
        self.time_collections = self.set_reference_time(
            self.time_run, self.time_step,
            time_range_period=self.info_obj_analysis['time_period'],
            time_range_frequency=self.info_obj_analysis['time_frequency'])

        self.obj_fields_data_name = [
            tag_var_compute, tag_var_name, tag_var_sf,
            tag_file_name, tag_folder_name, tag_file_compression,
            tag_file_type, tag_file_fields, tag_file_coords,
            tag_file_delimiter, tag_file_decimal_precision, tag_file_date_format, tag_file_date_order, tag_file_no_data]
        self.obj_fields_data_default = [
            False, 'NA', 1.0,
            None, None, False,
            'ascii', None, None,
            ';', 2, '%Y-%m-%d %H:%M', 'ascending', -9999.0]

        self.src_collections = {}
        for variable_name in self.info_obj_variable:
            var_obj = self.src_obj[variable_name]
            var_fields = define_file_fields(
                var_obj,
                obj_fields_list=self.obj_fields_data_name, obj_fields_default=self.obj_fields_data_default)
            self.src_collections[variable_name] = var_fields

        self.anc_collections = define_file_fields(
            self.anc_obj,
            obj_fields_list=self.obj_fields_data_name, obj_fields_default=self.obj_fields_data_default)

        self.dst_collections = define_file_fields(
            self.dst_obj,
            obj_fields_list=self.obj_fields_data_name, obj_fields_default=self.obj_fields_data_default)

        # --------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to set reference time information
    @staticmethod
    def set_reference_time(time_run=None, time_step=None,
                           time_data_period=0, time_data_frequency='H', time_data_rounding='H',
                           time_range_period=0, time_range_frequency='D', time_range_rounding='D',
                           time_reverse=False, time_key='max'):

        if time_data_period == 0:
            time_data_period = 1
        if time_range_period == 0:
            time_range_period = 1

        # set time range end
        if time_run > time_step:
            time_range_end = time_run
        else:
            time_range_end = time_step

        # set time range start
        time_range_idx = pd.date_range(end=time_range_end, periods=time_range_period, freq=time_range_frequency)
        time_range_start = time_range_idx[0]
        time_range_start = time_range_start.floor(time_range_rounding)

        # time data period
        time_data_idx = pd.date_range(start=time_range_start, end=time_range_end, freq=time_data_frequency)
        if time_reverse:
            time_data_idx = time_data_idx[::-1]
        # time data group
        time_data_groups = time_data_idx.to_period(time_range_frequency)
        time_data_chunks = time_data_idx.groupby(time_data_groups)

        if time_reverse:
            time_keys = list(time_data_chunks.keys())[::-1]
        else:
            time_keys = list(time_data_chunks.keys())

        time_data_collections = {}
        for time_step_key in time_keys:
            time_values = time_data_chunks[time_step_key]
            if time_key == 'reference':
                time_step_select = time_step_key.start_time
            elif time_key == 'max':
                time_step_select = time_values.max()
            elif time_key == 'min':
                time_step_select = time_values.min()
            else:
                log_stream.error(' ===> Time key "' + time_key + '" is not allowed')
                raise RuntimeError('Check the key to select the reference time')

            time_data_collections[time_step_select] = time_values

        return time_data_collections

    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to set reference geo information
    @staticmethod
    def set_reference_geo(geo_dict, var_name='grid'):
        geo_obj = geo_dict[var_name]
        return geo_obj
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to clean dynamic tmp
    def clean_dynamic_tmp(self, dynamic_file_collections):
        # remove dynamic tmp file(s)
        reset_dynamic_tmp = self.reset_dynamic_tmp
        if reset_dynamic_tmp:
            # iterate over tmp file path(s)
            for var_key, var_collections in dynamic_file_collections.items():
                for var_time_step, var_file_list in var_collections.items():
                    for var_file_path in var_file_list:
                        if os.path.exists(var_file_path):
                            os.remove(var_file_path)
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to dump dynamic data
    def dump_dynamic_data(self, dynamic_data_collections):

        # get time run
        time_run_stamp = self.time_run
        time_run_str = time_run_stamp.strftime(time_format_algorithm)

        # data collections
        dst_collections = self.dst_collections

        # get source file path(s)
        var_file_path_dst_raw = dst_collections['file_path']
        var_file_decimal_precision = dst_collections[tag_file_decimal_precision]
        var_file_delimiter = dst_collections[tag_file_delimiter]
        var_file_no_data = dst_collections[tag_file_no_data]
        var_file_index_format = dst_collections[tag_file_date_format]
        var_file_index_order = dst_collections[tag_file_date_order]

        # info algorithm start
        log_stream.info(' ---> Dump dynamic datasets [' + time_run_str + '] ... ')

        # check destination format
        if dst_collections[tag_file_type] == 'csv_2d':

            # iterate over dynamic datasets (according to the variable)
            for var_key, var_collections in dynamic_data_collections.items():

                # info variable start
                log_stream.info(' ----> Save variable "' + var_key + '"  ... ')

                # compose destination file name(s)
                var_file_path_dst_filled = define_file_name(
                    var_file_path_dst_raw,
                    file_template_keys={**self.template_obj_time, **self.template_obj_info},
                    file_template_values={
                        'run_sub_path_datetime': time_run_stamp,
                        'run_datetime': time_run_stamp,
                        'destination_sub_path_datetime': time_run_stamp,
                        'destination_datetime': time_run_stamp,
                        'var_name': var_key}
                )

                # check var collections availability
                if var_collections is not None:

                    # write file data in csv 2d format
                    folder_name_dst, file_name_dst = os.path.split(var_file_path_dst_filled)
                    os.makedirs(folder_name_dst, exist_ok=True)

                    write_file_csv(var_file_path_dst_filled, var_collections,
                                   dframe_sep=var_file_delimiter, dframe_decimal='.',
                                   dframe_float_format='%.{:}f'.format(var_file_decimal_precision),
                                   dframe_index=True, dframe_header=True,
                                   dframe_index_label=time_var_name, dframe_index_format=var_file_index_format,
                                   dframe_index_order=var_file_index_order,
                                   dframe_no_data=var_file_no_data)

                    # info variable end
                    log_stream.info(' ----> Save variable "' + var_key + '"  ... DONE')
                else:
                    # info variable end
                    log_stream.warning(' ===> Variable "' + var_key + '" has no data available')
                    log_stream.info(' ----> Save variable "' + var_key + '" ... SKIPPED')

        else:
            # exit for not allowed destination format
            log_stream.error(' ===> Destination format "' + dst_collections[tag_file_type] + '" is not allowed')
            raise NotImplementedError('Case not implemented yet')

        # info algorithm end
        log_stream.info(' ---> Dump dynamic datasets [' + time_run_str + '] ... DONE')

    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to compose dynamic data
    def compose_dynamic_data(self, dynamic_file_collections):

        # get time run
        time_run_stamp = self.time_run
        time_run_str = time_run_stamp.strftime(time_format_algorithm)

        # data collections
        dst_collections = self.dst_collections

        # info algorithm start
        log_stream.info(' ---> Compose dynamic datasets [' + time_run_str + '] ... ')

        # check destination format
        if dst_collections[tag_file_type] == 'csv_2d':

            # iterate over dynamic datasets (according to the variable)
            dynamic_data_collections = {}
            for var_key, var_collections in dynamic_file_collections.items():

                # info variable start
                log_stream.info(' ----> Extract variable "' + var_key + '"  ... ')

                # iterate over time keys and file list
                ws_data_var = None
                for time_key, file_list in var_collections.items():

                    # organize datasets in a unique dataframe by point(s)
                    ws_data_var = None
                    for file_path in file_list:

                        # read file data
                        if os.path.exists(file_path):
                            file_data = read_obj(file_path)
                        else:
                            log_stream.error(' ===> File "' + file_path + '" is not available')
                            raise IOError('File not found')

                        # organize the point(s) dataframe
                        if ws_data_var is None:
                            ws_data_var = deepcopy(file_data)
                        else:
                            columns_data = file_data.columns
                            ws_data_var = ws_data_var.join(file_data[columns_data].set_axis(ws_data_var.index))

                # manage dataframe: (1) order by columns and (2) set index name
                ws_data_var = ws_data_var.reindex(sorted(ws_data_var.columns), axis=1)
                ws_data_var.index.name = time_var_name

                # check data availability
                ws_data_check = ws_data_var.dropna(how="all")
                if ws_data_check.empty:
                    # store datasets in a collections
                    dynamic_data_collections[var_key] = None
                    # info variable end
                    log_stream.warning(' ===> Variable "' + var_key + '" has no data available')
                    log_stream.info(' ----> Extract variable "' + var_key + '" ... SKIPPED')
                else:
                    # store datasets in a collections
                    dynamic_data_collections[var_key] = ws_data_var
                    # info variable end
                    log_stream.info(' ----> Extract variable "' + var_key + '" ... DONE')

        else:
            # exit for not allowed destination format
            log_stream.error(' ===> Destination format "' + dst_collections[tag_file_type] + '" is not allowed')
            raise NotImplementedError('Case not implemented yet')

        # info algorithm end
        log_stream.info(' ---> Compose dynamic datasets [' + time_run_str + '] ... DONE')

        return dynamic_data_collections

    # -------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # method to get dynamic datasets
    def get_dynamic_data(self):

        # get time run
        time_run_stamp = self.time_run
        time_run_str = time_run_stamp.strftime(time_format_algorithm)

        # info algorithm start
        log_stream.info(' ---> Get dynamic datasets [' + time_run_str + '] ... ')

        # get info domain
        info_obj_domain = self.info_obj_domain

        # get geo collections
        geo_collections_grid = self.geo_collections_grid
        geo_collections_point = self.geo_collections_point
        # get time collections
        time_collections = self.time_collections
        # data collections
        src_collections = self.src_collections
        anc_collections = self.anc_collections

        # flags to reset
        reset_dynamic_data = self.reset_dynamic_data
        reset_dynamic_tmp = self.reset_dynamic_tmp

        # get ancillary file path(s)
        file_path_anc_raw = anc_collections['file_path']

        # iterate over domain(s)
        dynamic_file_collections = {}
        for domain_name in info_obj_domain:

            # info domain start
            log_stream.info(' ----> Domain "' + domain_name + '" ... ')

            # get point domain geo object(s)
            geo_points = geo_collections_point[domain_name]
            # get grid domain geo object(s)
            file_path_geo = geo_collections_grid[domain_name]
            if os.path.exists(file_path_geo):
                geo_obj_domain = read_obj(file_path_geo)
                geo_grid_values = geo_obj_domain['values']
                geo_grid_x_domain, geo_grid_y_domain = geo_obj_domain[geo_var_name_x], geo_obj_domain[geo_var_name_y]
                geo_grid_attrs_domain = None
            else:
                log_stream.error(' ===> Domain file "' + file_path_geo + '" is not available')
                raise IOError('Geographical domain file not found')

            # iterate over variable(s)
            for var_key, var_fields in src_collections.items():

                # info variable start
                log_stream.info(' -----> Variable "' + var_key + '" ... ')

                # get source file path(s)
                var_file_path_src_raw = src_collections[var_key]['file_path']
                var_compute = src_collections[var_key][tag_var_compute]
                var_name = src_collections[var_key][tag_var_name]
                var_scale_factor = src_collections[var_key][tag_var_sf]
                file_compression = src_collections[var_key][tag_file_compression]
                file_type = src_collections[var_key][tag_file_type]
                file_coords = src_collections[var_key][tag_file_coords]

                # check if variable is activated
                if var_compute:

                    # iterate over time chunk(s)
                    var_df_anc = None
                    for time_key_stamp, time_values in time_collections.items():

                        # info time reference start
                        time_key_str = time_key_stamp.strftime(time_format_algorithm)
                        log_stream.info(' ------> Time reference "' + time_key_str + '" ... ')

                        # compose ancillary file name(s)
                        file_path_anc_filled = define_file_name(
                            file_path_anc_raw,
                            file_template_keys={**self.template_obj_time, **self.template_obj_info},
                            file_template_values={
                                'run_sub_path_datetime': time_key_stamp,
                                'run_datetime': time_key_stamp,
                                'ancillary_sub_path_datetime': time_key_stamp,
                                'ancillary_datetime': time_key_stamp,
                                'var_name': var_key,
                                'domain_name': domain_name}
                        )

                        # store ancillary file name(s)
                        if var_key not in list(dynamic_file_collections.keys()):
                            dynamic_file_collections[var_key] = {}

                        if time_key_stamp not in list(dynamic_file_collections[var_key].keys()):
                            dynamic_file_collections[var_key][time_key_stamp] = [file_path_anc_filled]
                        else:
                            tmp_path_anc = dynamic_file_collections[var_key][time_key_stamp]
                            tmp_path_anc.extend([file_path_anc_filled])
                            dynamic_file_collections[var_key][time_key_stamp] = tmp_path_anc

                        # remove ancillary file(s)
                        if reset_dynamic_data:
                            if os.path.exists(file_path_anc_filled):
                                os.remove(file_path_anc_filled)

                        # check if ancillary file(s) are available
                        if not os.path.exists(file_path_anc_filled):

                            # iterate over time step(s)
                            for time_step_stamp in time_values:

                                # info time step start
                                time_step_str = time_step_stamp.strftime(time_format_algorithm)
                                log_stream.info(' -------> Time step "' + time_step_str + '" ... ')

                                # compose source file name(s)
                                var_file_path_src_filled_in = define_file_name(
                                    var_file_path_src_raw,
                                    file_template_keys={**self.template_obj_time, **self.template_obj_info},
                                    file_template_values={
                                        'run_sub_path_datetime': time_key_stamp,
                                        'run_datetime': time_key_stamp,
                                        'source_sub_path_datetime': time_step_stamp,
                                        'source_datetime': time_step_stamp,
                                        'var_name': var_key,
                                        'domain_name': domain_name}
                                )

                                # check source file(s)
                                if os.path.exists(var_file_path_src_filled_in):

                                    # check compression and unzip file(s)
                                    if file_compression:
                                        var_file_path_src_filled_out = define_file_unzip(var_file_path_src_filled_in)
                                        unzip_filename(var_file_path_src_filled_in, var_file_path_src_filled_out)
                                    else:
                                        var_file_path_src_filled_out = deepcopy(var_file_path_src_filled_in)

                                    # check file type and read data
                                    if file_type == 'netcdf':

                                        # get data grid in netcdf format
                                        var_da_src_step = read_data_nc(
                                            var_file_path_src_filled_out,
                                            geo_grid_x_domain, geo_grid_y_domain, geo_grid_attrs_domain,
                                            var_coords=file_coords,
                                            var_scale_factor=var_scale_factor,
                                            var_name=var_name,
                                            var_time=time_step_stamp,
                                            coord_name_geo_x=geo_coord_name_x, coord_name_geo_y=geo_coord_name_y,
                                            coord_name_time=time_coord_name,
                                            dim_name_geo_x=geo_dim_name_x, dim_name_geo_y=geo_dim_name_y,
                                            dim_name_time=time_dim_name,
                                            dims_order=[geo_dim_name_y, geo_dim_name_x, time_dim_name],
                                            decimal_round=2)

                                    elif file_type == 'tiff':

                                        # get data grid in tiff format
                                        var_da_src_step = read_data_tiff(
                                            var_file_path_src_filled_out,
                                            var_scale_factor=var_scale_factor, var_name=var_name,
                                            var_time=time_step_stamp,
                                            coord_name_geo_x=geo_coord_name_x, coord_name_geo_y=geo_coord_name_y,
                                            coord_name_time=time_coord_name,
                                            dim_name_geo_x=geo_dim_name_x, dim_name_geo_y=geo_dim_name_y,
                                            dim_name_time=time_dim_name,
                                            dims_order=[geo_dim_name_y, geo_dim_name_x, time_dim_name],
                                            decimal_round_data=2, decimal_round_geo=7)

                                    else:
                                        log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                                        '" ... FAILED')
                                        log_stream.error(' ===> File type "' + file_type + '"is not allowed.')
                                        raise NotImplementedError('Case not implemented yet')

                                    ''' debug dataset
                                    plt.figure(1); plt.imshow(var_da_src.values[:, :, 0]); plt.colorbar()
                                    plt.figure(2); plt.imshow(geo_values); plt.colorbar()
                                    plt.show()
                                    '''

                                    # delete uncompressed file(s)
                                    if reset_dynamic_tmp:
                                        if file_compression:
                                            if (os.path.exists(var_file_path_src_filled_in) and
                                                    os.path.exists(var_file_path_src_filled_out)):
                                                os.remove(var_file_path_src_filled_out)

                                    # info time step end
                                    log_stream.info(' -------> Time step "' + time_step_str +
                                                    '" ... DONE')

                                else:
                                    # info time step end
                                    var_da_src_step = None
                                    log_stream.info(' -------> Time step "' + time_step_str +
                                                    '" ... SKIPPED. File not found')

                                # extract data point
                                var_df_src_step = extract_data_point(time_step_stamp, var_da_src_step,
                                                                     geo_grid_values, geo_points)
                                # combine point dataframe
                                var_df_anc = combine_data_point(var_df_src_step, var_df_anc)

                            # save ancillary file(s)
                            folder_name_anc, file_name_anc = os.path.split(file_path_anc_filled)
                            os.makedirs(folder_name_anc, exist_ok=True)

                            write_obj(file_path_anc_filled, var_df_anc)

                            # info time reference end
                            log_stream.info(' ------> Time reference "' + time_key_str +
                                            '" ... DONE')

                        else:

                            # info time reference end
                            log_stream.info(' ------> Time reference "' + time_key_str +
                                            '" ... SKIPPED. Datasets previously saved')

                # info variable end
                log_stream.info(' -----> Variable "' + var_key + '" ... DONE')

            # info domain end
            log_stream.info(' ----> Domain "' + domain_name + '" ... DONE')

        # info algorithm end
        log_stream.info(' ---> Get dynamic datasets [' + time_run_str + '] ... DONE')

        return dynamic_file_collections

    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
