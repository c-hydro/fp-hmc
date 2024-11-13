"""
Class Features

Name:          driver_data_io_dynamic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os
import numpy as np
import pandas as pd
import xarray as xr

from copy import deepcopy

from tools.processing_tool_source2nc_converter.lib_data_io_binary import read_data_binary
from tools.processing_tool_source2nc_converter.lib_data_io_tiff import read_data_tiff
from tools.processing_tool_source2nc_converter.lib_data_io_nc import read_data_nc, write_data_nc

from tools.processing_tool_source2nc_converter.lib_utils_interp import active_var_interp, apply_var_interp
from tools.processing_tool_source2nc_converter.lib_utils_io import read_obj, write_obj, create_dset, write_dset
from tools.processing_tool_source2nc_converter.lib_utils_gzip import unzip_filename, zip_filename
from tools.processing_tool_source2nc_converter.lib_utils_system import fill_tags2string, make_folder
from tools.processing_tool_source2nc_converter.lib_info_args import logger_name, \
    time_format_algorithm, zip_extension

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
######################################################################################

# -------------------------------------------------------------------------------------
# Default definition(s)
var_fields_accepted = [
    "var_compute", "var_name", "var_scale_factor",
    "folder_name", "file_name", "file_compression", "file_type", "file_frequency"]
time_format_reference = '%Y-%m-%d'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Class DriverDynamic
class DriverDynamic:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_reference, time_period,
                 src_dict, anc_dict=None, dst_dict=None,
                 static_data_collection=None, interp_method='nearest',
                 alg_ancillary=None, alg_template_tags=None,
                 tag_terrain_data='Terrain', tag_grid_data='Grid',
                 tag_static_source='source', tag_static_destination='destination',
                 tag_dynamic_source='source', tag_dynamic_destination='destination',
                 flag_cleaning_dynamic_ancillary=True, flag_cleaning_dynamic_data=True, flag_cleaning_dynamic_tmp=True):

        self.time_str = time_reference.strftime(time_format_reference)
        self.time_period = time_period

        self.src_dict = src_dict
        self.anc_dict = anc_dict
        self.dst_dict = dst_dict

        self.tag_terrain_data = tag_terrain_data
        self.tag_grid_data = tag_grid_data

        self.tag_static_source = tag_static_source
        self.tag_static_destination = tag_static_destination
        self.tag_dynamic_source = tag_dynamic_source
        self.tag_dynamic_destination = tag_dynamic_destination

        self.alg_ancillary = alg_ancillary
        self.alg_template_tags = alg_template_tags

        if 'datasets_type' in list(self.alg_ancillary.keys()):
            self.alg_datasets_type = self.alg_ancillary['datasets_type']
        else:
            self.alg_datasets_type = 'forcing_data'

        self.static_data_src = static_data_collection[self.tag_static_source]
        self.static_data_dst = static_data_collection[self.tag_static_destination]

        self.var_compute_tag = 'var_compute'
        self.var_name_tag = 'var_name'
        self.var_scale_factor_tag = 'var_scale_factor'
        self.var_format_tag = 'var_format'
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'
        self.file_compression_tag = 'file_compression'
        self.file_geo_reference_tag = 'file_geo_reference'
        self.file_type_tag = 'file_type'
        self.file_coords_tag = 'file_coords'
        self.file_frequency_tag = 'file_frequency'
        self.file_time_steps_expected_tag = 'file_time_steps_expected'
        self.file_time_steps_ref_tag = 'file_time_steps_ref'
        self.file_time_steps_flag_tag = 'file_time_steps_flag'

        self.alg_template_list = list(self.alg_template_tags.keys())
        self.var_name_obj = self.define_var_name(src_dict)
        self.file_path_obj_src = self.define_file_name_struct(self.src_dict, self.var_name_obj, self.time_period)
        self.file_path_obj_dst = self.define_file_name_struct(self.dst_dict, 'all', self.time_period)['all']
        self.file_path_obj_anc = self.define_file_name_struct(self.anc_dict, 'all', self.time_period)['all']

        self.flag_cleaning_dynamic_ancillary = flag_cleaning_dynamic_ancillary
        self.flag_cleaning_dynamic_data = flag_cleaning_dynamic_data
        self.flag_cleaning_dynamic_tmp = flag_cleaning_dynamic_tmp

        if self.alg_datasets_type == 'forcing_data':
            self.coord_name_geo_x = 'longitude'
            self.coord_name_geo_y = 'latitude'
            self.coord_name_time = 'time'
            self.dim_name_geo_x = 'longitude'
            self.dim_name_geo_y = 'latitude'
            self.dim_name_time = 'time'
        elif self.alg_datasets_type == 'restart_data':
            self.coord_name_geo_x = 'Longitude'
            self.coord_name_geo_y = 'Latitude'
            self.coord_name_time = 'time'
            self.dim_name_geo_x = 'west_east'
            self.dim_name_geo_y = 'south_north'
            self.dim_name_time = 'time'
        else:
            log_stream.error(' ===> Datasets type ' + self.alg_datasets_type + ' is not allowed.')
            raise IOError('Check your datasets type in the configuration file.')

        self.dims_order_2d = [self.dim_name_geo_y, self.dim_name_geo_x]
        self.dims_order_3d = [self.dim_name_geo_y, self.dim_name_geo_x, self.dim_name_time]
        self.coord_order_2d = [self.coord_name_geo_y, self.coord_name_geo_x]
        self.coord_order_3d = [self.coord_name_geo_y, self.coord_name_geo_x, self.coord_name_time]

        self.geo_da_dst = self.set_geo_reference()

        self.interp_method = interp_method

        self.nc_compression_level = 9
        self.nc_type_file = 'NETCDF4'
        self.nc_type_engine = 'netcdf4'

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set geographical reference
    def set_geo_reference(self):

        geo_ref_name = self.dst_dict[self.file_geo_reference_tag]
        geo_ref_collections = self.static_data_dst[geo_ref_name]

        geo_ref_data = geo_ref_collections['data']
        geo_ref_coord_x = geo_ref_collections['geo_x']
        geo_ref_coord_y = geo_ref_collections['geo_y']

        geo_ref_nrows = geo_ref_collections['nrows']
        geo_ref_ncols = geo_ref_collections['ncols']
        geo_ref_xll_corner = geo_ref_collections['xllcorner']
        geo_ref_yll_corner = geo_ref_collections['yllcorner']
        geo_ref_cellsize = geo_ref_collections['cellsize']
        geo_ref_nodata = geo_ref_collections['nodata_value']

        geo_ref_coord_x_2d, geo_ref_coord_y_2d = np.meshgrid(geo_ref_coord_x, geo_ref_coord_y)

        geo_y_upper = geo_ref_coord_y_2d[0, 0]
        geo_y_lower = geo_ref_coord_y_2d[-1, 0]
        if geo_y_lower > geo_y_upper:
            geo_ref_coord_y_2d = np.flipud(geo_ref_coord_y_2d)
            geo_ref_data = np.flipud(geo_ref_data)

        geo_da = xr.DataArray(
            geo_ref_data, name=geo_ref_name, dims=self.dims_order_2d,
            coords={self.coord_name_geo_x: (self.dim_name_geo_x, geo_ref_coord_x_2d[0, :]),
                    self.coord_name_geo_y: (self.dim_name_geo_y, geo_ref_coord_y_2d[:, 0])})

        geo_da.attrs = {'ncols': geo_ref_ncols, 'nrows': geo_ref_nrows,
                        'nodata_value': geo_ref_nodata,
                        'xllcorner': geo_ref_xll_corner, 'yllcorner': geo_ref_yll_corner,
                        'cellsize': geo_ref_cellsize}

        return geo_da
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set geographical attributes
    @staticmethod
    def set_geo_attributes(dict_info, tag_data='data', tag_geo_x='geo_x', tag_geo_y='geo_y', no_grid_message=True):

        if dict_info is not None:

            if tag_data in list(dict_info.keys()):
                data_values = dict_info[tag_data]
            else:
                log_stream.error(' ===> Tag "' + tag_data + '" is not available. Values are not found')
                raise IOError('Check your static datasets')
            if tag_geo_x in list(dict_info.keys()):
                data_geo_x = dict_info[tag_geo_x]
            else:
                log_stream.error(' ===> Tag "' + tag_geo_x + '" is not available. Values are not found')
                raise IOError('Check your static datasets')
            if tag_geo_y in list(dict_info.keys()):
                data_geo_y = dict_info[tag_geo_y]
            else:
                log_stream.error(' ===> Tag "' + tag_geo_y + '" is not available. Values are not found')
                raise IOError('Check your static datasets')

            data_attrs = deepcopy(dict_info)
            [data_attrs.pop(key) for key in [tag_data, tag_geo_x, tag_geo_y]]

        else:
            if no_grid_message:
                log_stream.warning(' ===> Static datasets are not available. Values are set as NoneType.'
                                   ' ALl information will be extracted from dynamic datasets')
            data_values, data_geo_x, data_geo_y, data_attrs = None, None, None, None

        return data_values, data_geo_x, data_geo_y, data_attrs
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define unzipped filename(s)
    @staticmethod
    def define_file_name_unzip(file_path_zip, file_extension_zip=None):

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

    # -------------------------------------------------------------------------------------
    # Method to define zipped filename(s)
    @staticmethod
    def define_file_name_zip(file_path_unzip, file_extension_zip=None):

        if file_extension_zip is None:
            file_extension_zip = zip_extension

        file_extension_zip = file_extension_zip.replace('.', '')

        if not file_path_unzip.endswith(file_extension_zip):
            file_path_zip = '.'.join([file_path_unzip, file_extension_zip])
        elif file_path_unzip.endswith(file_extension_zip):
            file_path_zip = file_path_unzip

        return file_path_zip
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define filename(s) struct
    def define_file_name_struct(self, var_dict, var_list, time_period):

        alg_template_tags = self.alg_template_tags

        if not isinstance(var_list, list):
            var_list = [var_list]

        file_path_dict = {}
        for var_name in var_list:

            if var_name in list(var_dict.keys()):
                folder_name_step = var_dict[var_name][self.folder_name_tag]
                file_name_step = var_dict[var_name][self.file_name_tag]
            else:
                folder_name_step = var_dict[self.folder_name_tag]
                file_name_step = var_dict[self.file_name_tag]

            file_path_step = os.path.join(folder_name_step, file_name_step)

            file_path_list = []
            for time_step in time_period:
                alg_template_filled = {}
                for alg_template_step in self.alg_template_list:
                    alg_template_filled[alg_template_step] = time_step
                file_path_list.append(fill_tags2string(file_path_step, alg_template_tags, alg_template_filled))

            file_path_dict[var_name] = file_path_list

        return file_path_dict

    # -------------------------------------------------------------------------------------
    # Method to define variable names
    @staticmethod
    def define_var_name(data_dict, data_fields_excluded=None):

        if data_fields_excluded is None:
            data_fields_excluded = ['__comment__', '_comment_', 'comment','']

        var_list_tmp = list(data_dict.keys())
        var_list_def = [var_name for var_name in var_list_tmp if var_name not in data_fields_excluded]

        return var_list_def
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to extract variable field(s)
    def extract_var_fields(self, var_dict):

        var_compute = var_dict[self.var_compute_tag]
        var_name = var_dict[self.var_name_tag]
        var_scale_factor = var_dict[self.var_scale_factor_tag]
        file_compression = var_dict[self.file_compression_tag]
        file_geo_reference = var_dict[self.file_geo_reference_tag]
        file_type = var_dict[self.file_type_tag]
        file_coords = var_dict[self.file_coords_tag]
        file_freq = var_dict[self.file_frequency_tag]

        if self.var_format_tag in list(var_dict.keys()):
            var_format = var_dict[self.var_format_tag]
        else:
            if file_type == 'binary':
                var_format = 'i'
            else:
                var_format = None

        if self.file_time_steps_expected_tag in list(var_dict.keys()):
            file_time_steps_expected = var_dict[self.file_time_steps_expected_tag]
        else:
            file_time_steps_expected = 1
        if self.file_time_steps_ref_tag in list(var_dict.keys()):
            file_time_steps_ref = var_dict[self.file_time_steps_ref_tag]
        else:
            file_time_steps_ref = 1
        if self.file_time_steps_flag_tag in list(var_dict.keys()):
            file_time_steps_flag = var_dict[self.file_time_steps_flag_tag]
        else:
            file_time_steps_flag = self.dim_name_time

        return var_compute, var_name, var_scale_factor, var_format, \
               file_compression, file_geo_reference, file_type, file_coords, file_freq, \
               file_time_steps_expected, file_time_steps_ref, file_time_steps_flag
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean dynamic tmp
    def clean_dynamic_tmp(self):

        flag_cleaning_tmp = self.flag_cleaning_dynamic_tmp
        file_path_anc = self.file_path_obj_anc

        if flag_cleaning_tmp:
            for file_path_step in file_path_anc:
                if os.path.exists(file_path_step):
                    os.remove(file_path_step)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to dump dynamic data
    def dump_dynamic_data(self):

        time_str = self.time_str
        time_period = self.time_period

        var_name_obj = self.var_name_obj
        src_dict = self.src_dict
        dst_dict = self.dst_dict

        file_path_obj_anc = self.file_path_obj_anc
        file_path_obj_dst = self.file_path_obj_dst

        datasets_type = self.alg_datasets_type

        flag_cleaning_dynamic = self.flag_cleaning_dynamic_data

        log_stream.info(' ---> Dump dynamic datasets [' + time_str + '] ... ')

        for time_step, file_path_anc, file_path_dst in zip(time_period, file_path_obj_anc, file_path_obj_dst):

            log_stream.info(' -----> Time "' + time_step.strftime(time_format_algorithm) + '" ... ')
            file_path_zip = self.define_file_name_zip(file_path_dst)

            if flag_cleaning_dynamic:
                if os.path.exists(file_path_dst):
                    os.remove(file_path_dst)
                if os.path.exists(file_path_zip):
                    os.remove(file_path_zip)

            if os.path.exists(file_path_anc):

                dset_obj = read_obj(file_path_anc)

                folder_name_dst, file_name_dst = os.path.split(file_path_dst)
                if not os.path.exists(folder_name_dst):
                    make_folder(folder_name_dst)

                log_stream.info(' ------> Save filename "' + file_name_dst + '" ... ')

                if not (os.path.exists(file_path_dst) or os.path.exists(file_path_zip)):

                    if datasets_type == 'forcing_data':

                        log_stream.info(' -------> Forcing datasets ... ')

                        # Squeeze time dimensions (if equal == 1)  continuum expects 2d variables in forcing variables
                        if self.dim_name_time in list(dset_obj.dims):
                            time_array = dset_obj[self.dim_name_time].values
                            if time_array.shape[0] == 1:
                                dset_obj = dset_obj.squeeze(self.dim_name_time)
                                dset_obj = dset_obj.drop(self.dim_name_time)

                        log_stream.info(' --------> Write datasets ... ')
                        write_dset(file_path_dst, dset_obj,
                                   dset_engine=self.nc_type_engine, dset_format=self.nc_type_file,
                                   dset_compression=self.nc_compression_level, fill_data=-9999.0, dset_type='float32')
                        log_stream.info(' --------> Write datasets ... DONE')

                        log_stream.info(' -------> Forcing datasets ... DONE')

                    elif datasets_type == 'restart_data':

                        log_stream.info(' -------> Restart datasets ... ')

                        var_data_dict = {}
                        var_dims_def = {}
                        var_dims_list = {}
                        for var_name in var_name_obj:

                            log_stream.info(' --------> Configure variable "' + var_name + '" ... ')

                            var_compute, var_tag, var_scale_factor, var_format, file_compression, \
                                file_geo_reference, file_type, file_coords, file_freq, \
                                file_time_steps_expected, \
                                file_time_steps_ref, file_time_steps_flag = self.extract_var_fields(src_dict[var_name])

                            if var_compute:

                                var_geo_data, var_geo_x, var_geo_y, var_geo_attrs = \
                                    self.set_geo_attributes(self.static_data_src[file_geo_reference])

                                if (var_geo_x.shape.__len__() == 1) and (var_geo_y.shape.__len__() == 1):
                                    var_geo_x_2d, var_geo_y_2d = np.meshgrid(var_geo_x, var_geo_y)
                                    if self.dim_name_geo_y not in list(var_dims_def.keys()):
                                        var_dims_def[self.dim_name_geo_y] = var_geo_y.shape[0]
                                    if self.dim_name_geo_x not in list(var_dims_def.keys()):
                                        var_dims_def[self.dim_name_geo_x] = var_geo_x.shape[0]

                                    if self.coord_name_geo_y not in list(var_data_dict.keys()):
                                        var_data_dict[self.coord_name_geo_y] = var_geo_y_2d
                                        var_dims_list[self.coord_name_geo_y] = deepcopy(self.dims_order_2d)
                                    if self.coord_name_geo_x not in list(var_data_dict.keys()):
                                        var_data_dict[self.coord_name_geo_x] = var_geo_x_2d
                                        var_dims_list[self.coord_name_geo_x] = deepcopy(self.dims_order_2d)
                                else:
                                    log_stream.error(' ===> Geographical dimensions are not allowed.')
                                    raise NotImplementedError('Case not implemented yet')

                                if file_time_steps_flag not in list(var_dims_def.keys()):
                                    var_dims_def[file_time_steps_flag] = file_time_steps_expected

                                var_dset = dset_obj[var_name]

                                if self.dim_name_time in list(var_dset.dims):
                                    time_array = var_dset[self.dim_name_time].values
                                    if time_array.shape[0] == 1:
                                        var_dset = var_dset.squeeze(self.dim_name_time)
                                        var_dset = var_dset.drop(self.dim_name_time)

                                        if self.dim_name_time not in list(var_dims_def.keys()):
                                            var_dims_def[self.dim_name_time] = None

                                var_data = np.flipud(var_dset[var_name].values)
                                var_data_dict[var_name] = var_data

                                if var_data.ndim == 2:
                                    dims_order_2d = deepcopy(self.dims_order_2d)
                                    var_dims_list[var_name] = dims_order_2d
                                elif var_data.ndim == 3:
                                    dims_order_3d = deepcopy(self.dims_order_3d)
                                    dims_order_3d[2] = file_time_steps_flag
                                    var_dims_list[var_name] = dims_order_3d
                                else:
                                    log_stream.error(' ===> Datasets dimensions for ' + var_name + ' is not allowed.')
                                    raise NotImplementedError('Case not implemented yet')

                                log_stream.info(' --------> Configure variable "' + var_name + '" ... DONE')

                            else:
                                log_stream.info(' --------> Configure variable "' +
                                                var_name + '" ... SKIPPED. Variable is not activated.')

                        log_stream.info(' --------> Write datasets ... ')
                        write_data_nc(file_path_dst, var_data_dict, var_dims_def,
                                      var_dims_list, var_geo_attrs, file_format=self.nc_type_file)
                        log_stream.info(' --------> Write datasets ... DONE')

                        log_stream.info(' -------> Restart datasets ... DONE')

                    else:
                        log_stream.error(' ===> Datasets type ' + datasets_type + ' is not allowed.')
                        raise IOError('Check your datasets type in the configuration file.')

                    log_stream.info(' ------> Save filename "' + file_name_dst + '" ... DONE')

                    log_stream.info(' ------> Zip filename "' + file_name_dst + '" ... ')
                    if dst_dict[self.file_compression_tag]:

                        zip_filename(file_path_dst, file_path_zip)

                        if os.path.exists(file_path_zip) and (file_path_zip != file_name_dst):
                            os.remove(file_path_dst)
                        log_stream.info(' ------> Zip filename "' + file_name_dst + '" ... DONE')
                    else:
                        log_stream.info(' ------> Zip filename "' + file_name_dst + '" ... SKIPPED. Zip not activated')
                else:
                    log_stream.info(' ------> Save filename "' + file_name_dst +
                                    '" ... SKIPPED. Filename previously saved')

                log_stream.info(' -----> Time "' + time_step.strftime(time_format_algorithm) + '" ... DONE')

            else:
                log_stream.info(' -----> Time "' + time_step.strftime(time_format_algorithm) +
                                '" ... SKIPPED. Datasets not available')

        log_stream.info(' ---> Dump dynamic datasets [' + time_str + '] ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize dynamic data
    def organize_dynamic_data(self):

        time_str = self.time_str
        time_period = self.time_period

        geo_da_dst = self.geo_da_dst

        src_dict = self.src_dict

        var_name_obj = self.var_name_obj
        file_path_obj_src = self.file_path_obj_src
        file_path_obj_anc = self.file_path_obj_anc

        datasets_type = self.alg_datasets_type

        flag_cleaning_ancillary = self.flag_cleaning_dynamic_ancillary

        log_stream.info(' ---> Organize dynamic datasets [' + time_str + '] ... ')

        file_check_list = []
        for file_path_tmp in file_path_obj_anc:
            if os.path.exists(file_path_tmp):
                if flag_cleaning_ancillary:
                    os.remove(file_path_tmp)
                    file_check_list.append(False)
                else:
                    file_check_list.append(True)
            else:
                file_check_list.append(False)
        file_check = all(file_check_list)

        # Check elements availability
        if not file_check:

            dset_collection = {}
            for var_name in var_name_obj:

                log_stream.info(' ----> Variable "' + var_name + '" ... ')

                var_compute, var_tag, var_scale_factor, var_format, file_compression, \
                    file_geo_reference, file_type, file_coords, file_freq, \
                    file_time_steps_expected, \
                    file_time_steps_ref, file_time_steps_flag = self.extract_var_fields(src_dict[var_name])
                var_file_path_src = file_path_obj_src[var_name]

                if var_compute:

                    no_grid_message, compare_message = True, True
                    var_geo_data, var_geo_x, var_geo_y, var_geo_attrs = None, None, None, None
                    for var_time, var_file_path_in in zip(time_period, var_file_path_src):

                        log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) + '" ... ')

                        if os.path.exists(var_file_path_in):

                            if file_compression:
                                var_file_path_out = self.define_file_name_unzip(var_file_path_in)
                                unzip_filename(var_file_path_in, var_file_path_out)
                            else:
                                var_file_path_out = deepcopy(var_file_path_in)

                            if file_type == 'binary':

                                if var_geo_data is None:
                                    log_stream.info(' ------> Select geo reference for binary datasets ... ')

                                    log_stream.info(' -------> Geo reference name: ' + file_geo_reference)
                                    var_geo_data, var_geo_x, var_geo_y, var_geo_attrs = \
                                        self.set_geo_attributes(self.static_data_src[file_geo_reference])
                                    log_stream.info(' ------> Select geo reference for binary datasets ... DONE')

                                if (var_geo_x is None) or (var_geo_y is None):
                                    log_stream.error(' ===> Geo reference is not defined for binary file case')
                                    raise IOError('Check your geo reference in the configuration file')

                                var_da_src = read_data_binary(
                                    var_file_path_out, var_geo_x, var_geo_y, var_geo_attrs,
                                    var_scale_factor=var_scale_factor, var_time=var_time,
                                    var_name=var_name, var_format=var_format,
                                    var_time_steps_expected=file_time_steps_expected,
                                    coord_name_geo_x=self.coord_name_geo_x, coord_name_geo_y=self.coord_name_geo_y,
                                    coord_name_time=self.coord_name_time,
                                    dim_name_geo_x=self.dim_name_geo_x, dim_name_geo_y=self.dim_name_geo_y,
                                    dim_name_time=self.dim_name_time,
                                    dims_order=self.dims_order_3d)

                            elif file_type == 'netcdf':

                                if var_geo_data is None:
                                    log_stream.info(' ------> Select geo reference for netcdf datasets ... ')
                                    var_geo_data, var_geo_x, var_geo_y, var_geo_attrs = \
                                        self.set_geo_attributes(self.static_data_src[file_geo_reference],
                                                                no_grid_message=no_grid_message)

                                    log_stream.info(' ------> Select geo reference for netcdf datasets ... DONE')

                                var_da_src = read_data_nc(
                                    var_file_path_out, var_geo_x, var_geo_y, var_geo_attrs,  var_coords=file_coords,
                                    var_scale_factor=var_scale_factor, var_name=var_tag, var_time=var_time,
                                    coord_name_geo_x=self.coord_name_geo_x, coord_name_geo_y=self.coord_name_geo_y,
                                    coord_name_time=self.coord_name_time,
                                    dim_name_geo_x=self.dim_name_geo_x, dim_name_geo_y=self.dim_name_geo_y,
                                    dim_name_time=self.dim_name_time,
                                    dims_order=self.dims_order_3d, compare_message=compare_message)

                                no_grid_message, compare_message = False, False

                            elif file_type == 'tiff':

                                var_da_src = read_data_tiff(
                                    var_file_path_out,
                                    var_scale_factor=var_scale_factor, var_name=var_tag, var_time=var_time,
                                    coord_name_geo_x=self.coord_name_geo_x, coord_name_geo_y=self.coord_name_geo_y,
                                    coord_name_time=self.coord_name_time,
                                    dim_name_geo_x=self.dim_name_geo_x, dim_name_geo_y=self.dim_name_geo_y,
                                    dim_name_time=self.dim_name_time,
                                    dims_order=self.dims_order_3d,
                                    decimal_round_data=2, decimal_round_geo=7)

                                '''
                                var_values = var_da_src[:, :, 0].values
                                plt.figure()
                                plt.imshow(var_values)
                                plt.colorbar()
                                plt.show()
                                '''

                            else:
                                log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) + '" ... FAILED')
                                log_stream.error(' ===> File type "' + file_type + '"is not allowed.')
                                raise NotImplementedError('Case not implemented yet')

                            # Delete (if needed the uncompressed file(s)
                            if var_file_path_in != var_file_path_out:
                                if os.path.exists(var_file_path_out):
                                    os.remove(var_file_path_out)

                            # Organize destination dataset
                            if var_da_src is not None:

                                # Active (if needed) interpolation method to the variable source data-array
                                active_interp = active_var_interp(var_da_src.attrs, geo_da_dst.attrs)

                                # Apply the interpolation method to the variable source data-array
                                if active_interp:
                                    var_da_dst = apply_var_interp(
                                        var_da_src, geo_da_dst,
                                        dim_name_geo_x=self.dim_name_geo_x, dim_name_geo_y=self.dim_name_geo_y,
                                        coord_name_geo_x=self.coord_name_geo_x, coord_name_geo_y=self.coord_name_geo_y,
                                        interp_method=self.interp_method)
                                else:
                                    if var_tag != var_name:
                                        var_da_dst = deepcopy(var_da_src)
                                        var_da_dst.name = var_name
                                    else:
                                        var_da_dst = deepcopy(var_da_src)

                                # Mask the variable destination data-array
                                var_nodata = None
                                if 'nodata_value' in list(var_da_dst.attrs.keys()):
                                    var_nodata = var_da_dst.attrs['nodata_value']
                                geo_nodata = None
                                if 'nodata_value' in list(geo_da_dst.attrs.keys()):
                                    geo_nodata = geo_da_dst.attrs['nodata_value']

                                if geo_nodata is not None and (var_nodata is not None):
                                    var_da_masked = var_da_dst.where(
                                        ((geo_da_dst.values[:, :, np.newaxis] != geo_nodata) != geo_nodata) &
                                        (var_da_dst != var_nodata))
                                else:
                                    var_da_masked = deepcopy(var_da_dst)

                                '''
                                plt.figure(1)
                                plt.imshow(var_da_dst[:, :, 0].values)
                                plt.colorbar()
                                plt.figure(2)
                                plt.imshow(var_da_src[:, :, 0].values)
                                plt.colorbar()
                                plt.figure(3)
                                plt.imshow(var_da_masked[:, :, 0].values)
                                plt.colorbar()
                                plt.figure(4)
                                plt.imshow(geo_da_dst.values)
                                plt.colorbar()
                                plt.show()
                                '''

                                # Organize data in a common datasets
                                if self.dim_name_time in list(var_da_masked.dims):
                                    var_time_dset = pd.DatetimeIndex(var_da_masked[self.dim_name_time].values)
                                else:
                                    var_time_dset = deepcopy(var_time)

                                var_dset_masked = create_dset(var_data_time=var_time_dset,
                                                              var_data_name=var_name, var_data_values=var_da_masked,
                                                              var_data_attrs=None,
                                                              var_geo_1d=False,
                                                              file_attributes=geo_da_dst.attrs,
                                                              var_geo_name='terrain',
                                                              var_geo_values=geo_da_dst.values,
                                                              var_geo_x=geo_da_dst[self.coord_name_geo_x].values,
                                                              var_geo_y=geo_da_dst[self.coord_name_geo_y].values,
                                                              var_geo_attrs=None)

                                # Organize data in merged datasets
                                if datasets_type == 'forcing_data':
                                    if var_time not in list(dset_collection.keys()):
                                        dset_collection[var_time] = var_dset_masked
                                    else:
                                        var_dset_tmp = deepcopy(dset_collection[var_time])
                                        var_dset_tmp = var_dset_tmp.merge(var_dset_masked, join='right')
                                        dset_collection[var_time] = var_dset_tmp
                                elif datasets_type == 'restart_data':
                                    if var_time not in list(dset_collection.keys()):
                                        dset_collection[var_time] = {}
                                    dset_collection[var_time][var_name] = {}
                                    dset_collection[var_time][var_name] = var_dset_masked
                                else:
                                    log_stream.error(' ===> Datasets type ' + datasets_type + ' is not allowed.')
                                    raise IOError('Check your datasets type in the configuration file.')

                                log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                                '" ... DONE')

                            else:
                                log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                                '" ... SKIPPED. Datasets is not defined')
                        else:
                            log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                            '" ... SKIPPED. File source "' + var_file_path_in + '" is not available')

                    log_stream.info(' ----> Variable "' + var_name + '" ... DONE')

                else:
                    log_stream.info(' ----> Variable "' + var_name + '" ... SKIPPED. Compute flag not activated.')

            # Save ancillary datasets
            for file_path_anc, (dset_time, dset_anc) in zip(file_path_obj_anc, dset_collection.items()):

                folder_name_anc, file_name_anc = os.path.split(file_path_anc)
                if not os.path.exists(folder_name_anc):
                    make_folder(folder_name_anc)

                write_obj(file_path_anc, dset_anc)

            log_stream.info(' ---> Organize dynamic datasets [' + time_str + '] ... DONE')
        else:
            log_stream.info(' ---> Organize dynamic datasets [' +
                            time_str + '] ... SKIPPED. All datasets are previously computed')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
