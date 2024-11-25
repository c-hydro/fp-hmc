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
import xarray as xr

from copy import deepcopy

from tools.processing_tool_datasets_merger.lib_data_io_nc import read_data_nc
from tools.processing_tool_datasets_merger.lib_data_io_tiff import read_data_tiff
from tools.processing_tool_datasets_merger.lib_data_io_remap import create_dset_continuum

from tools.processing_tool_datasets_merger.lib_utils_method_interpolate import active_var_interpolate, \
    apply_var_interpolate, apply_var_sample
from tools.processing_tool_datasets_merger.lib_utils_method_mask import active_var_mask, \
    apply_var_mask
from tools.processing_tool_datasets_merger.lib_utils_io import read_obj, write_obj, write_dset_nc, write_dset_tiff, \
    filter_dset_vars, adjust_dset_vars
from tools.processing_tool_datasets_merger.lib_utils_gzip import unzip_filename, zip_filename
from tools.processing_tool_datasets_merger.lib_utils_system import fill_tags2string, make_folder, intersect_dicts, find_folder
from tools.processing_tool_datasets_merger.lib_info_args import logger_name, \
    time_format_algorithm, zip_extension

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverDynamic
class DriverDynamic:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_reference, time_period,
                 src_dict, anc_dict=None, dst_dict=None,
                 static_data_collection=None,
                 alg_ancillary=None, alg_template_tags=None, alg_datasets_type='generic',
                 tag_terrain_data='Terrain', tag_grid_data='Grid',
                 tag_static_source='source', tag_static_destination='destination',
                 tag_dynamic_source='source', tag_dynamic_destination='destination',
                 flag_cleaning_dynamic_ancillary=True, flag_cleaning_dynamic_data=True, flag_cleaning_dynamic_tmp=True):

        self.time_reference = time_reference
        self.time_period = time_period
        self.time_str = self.time_reference.strftime(time_format_algorithm)

        self.src_dict = src_dict
        self.anc_dict = anc_dict
        self.dst_dict = dst_dict

        self.tag_terrain_data = tag_terrain_data
        self.tag_grid_data = tag_grid_data

        self.tag_static_source = tag_static_source
        self.tag_static_destination = tag_static_destination
        self.tag_dynamic_source = tag_dynamic_source
        self.tag_dynamic_destination = tag_dynamic_destination

        self.tag_domain_name = 'domain_name'
        self.tag_layer_name = 'layer_name'
        self.tag_layer_scale_factor = 'layer_scale_factor'
        self.tag_layer_no_data = 'layer_no_data'
        self.tag_layer_nc_format = 'layer_nc_format'

        alg_layer_variable = alg_ancillary[self.tag_layer_name]
        if not isinstance(alg_layer_variable, list):
            alg_layer_variable = [alg_layer_variable]
        self.alg_layer_variable = alg_layer_variable

        alg_layer_scale_factor = alg_ancillary[self.tag_layer_scale_factor]
        if not isinstance(alg_layer_scale_factor, list):
            alg_layer_scale_factor = [alg_layer_scale_factor]
        self.alg_layer_scale_factor = alg_layer_scale_factor

        alg_layer_no_data = alg_ancillary[self.tag_layer_no_data]
        if not isinstance(alg_layer_no_data, list):
            alg_layer_no_data = [alg_layer_no_data]
        self.alg_layer_no_data = alg_layer_no_data

        alg_domain_name = alg_ancillary[self.tag_domain_name]
        if not isinstance(alg_domain_name, list):
            alg_domain_name = [alg_domain_name]
        self.alg_domain_name = alg_domain_name

        if self.tag_layer_nc_format in list(alg_ancillary.keys()):
            self.alg_layer_nc_format = alg_ancillary[self.tag_layer_nc_format]
        else:
            self.alg_layer_nc_format = 'continuum'

        # if self.tag_layer_fx_merging in list(alg_ancillary.keys()):
        #     self.alg_layer_fx_merging = alg_ancillary[self.tag_layer_fx_merging]
        # else:
        #     alg_layer_fx_merging = [{"fx": "interpolate", "method": "nearest"}]
        #     self.alg_layer_fx_merging = alg_layer_fx_merging * self.alg_layer_variable.__len__()

        self.alg_template_time = alg_template_tags['time']
        self.alg_template_data = alg_template_tags['data']

        self.static_data_src = static_data_collection[self.tag_static_source]
        self.static_data_dst = static_data_collection[self.tag_static_destination]

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'
        self.file_include_tag = 'file_include'
        self.file_compression_tag = 'file_compression'
        self.file_geo_reference_tag = 'file_geo_reference'
        self.file_geo_mask_tag = 'file_geo_mask'
        self.file_type_tag = 'file_type'
        self.file_coords_tag = 'file_coords'
        self.file_frequency_tag = 'file_frequency'
        self.file_domain_tag = 'file_domain'
        self.file_layer_tag = 'file_layer'
        self.file_time_steps_expected_tag = 'file_time_steps_expected'
        self.file_time_steps_ref_tag = 'file_time_steps_ref'
        self.file_time_steps_flag_tag = 'file_time_steps_flag'

        self.var_name_src = self.define_var_name(src_dict)
        self.var_name_dst = self.define_var_name(dst_dict)
        self.var_name_anc = self.define_var_name(anc_dict)

        self.file_path_obj_src = self.define_file_name_struct(
            self.src_dict, self.var_name_src, var_time_period=time_period, flag_check_domain=True)
        self.file_path_obj_dst = self.define_file_name_struct(
            self.dst_dict, self.var_name_dst, var_time_period=time_period, flag_check_domain=False)
        self.file_path_obj_anc = self.define_file_name_struct(
            self.anc_dict, self.var_name_anc, var_time_period=time_period, flag_check_domain=False)

        self.alg_datasets_type = alg_datasets_type
        if self.alg_datasets_type == 'generic':
            self.coord_name_geo_x = 'longitude'
            self.coord_name_geo_y = 'latitude'
            self.coord_name_time = 'time'
            self.dim_name_geo_x = 'longitude'
            self.dim_name_geo_y = 'latitude'
            self.dim_name_time = 'time'
        else:
            log_stream.error(' ===> Datasets type ' + self.alg_datasets_type + ' is not allowed.')
            raise IOError('Check your datasets type in the configuration file.')

        self.dims_order_2d = [self.dim_name_geo_y, self.dim_name_geo_x]
        self.dims_order_3d = [self.dim_name_geo_y, self.dim_name_geo_x, self.dim_name_time]
        self.coord_order_2d = [self.coord_name_geo_y, self.coord_name_geo_x]
        self.coord_order_3d = [self.coord_name_geo_y, self.coord_name_geo_x, self.coord_name_time]

        self.geo_anc_tag, self.geo_anc_data = self.select_geo_reference(anc_dict, self.static_data_src)
        self.geo_anc_da = self.set_geo_reference(self.geo_anc_data, self.geo_anc_tag)

        self.geo_dst_tag, self.geo_dst_data = self.select_geo_reference(dst_dict, self.static_data_dst)
        self.geo_dst_da = self.set_geo_reference(self.geo_dst_data, self.geo_dst_tag)

        self.method_interpolate_source = 'nearest'
        if 'layer_method_interpolate_source' in list(alg_ancillary.keys()):
            self.method_interpolate_source = alg_ancillary['layer_method_interpolate_source']
        self.method_interpolate_destination = 'nearest'
        if 'layer_method_interpolate_destination' in list(alg_ancillary.keys()):
            self.method_interpolate_destination = alg_ancillary['layer_method_interpolate_destination']

        self.method_mask_source = None
        if 'layer_method_mask_source' in list(alg_ancillary.keys()):
            self.method_mask_source = alg_ancillary['layer_method_mask_source']
        self.method_mask_destination = None
        if 'layer_method_mask_destination' in list(alg_ancillary.keys()):
            self.method_mask_destination = alg_ancillary['layer_method_mask_destination']

        self.nc_compression_level = 9
        self.nc_type_file = 'NETCDF4'
        self.nc_type_engine = 'netcdf4'

        self.tiff_compression_option = 'COMPRESS=DEFLATE'

        self.flag_cleaning_dynamic_ancillary = flag_cleaning_dynamic_ancillary
        self.flag_cleaning_dynamic_data = flag_cleaning_dynamic_data
        self.flag_cleaning_dynamic_tmp = flag_cleaning_dynamic_tmp

        self.file_check_ancillary = self.check_file_collections(
            self.file_path_obj_anc, self.flag_cleaning_dynamic_ancillary)
        self.file_check_destination = self.check_file_collections(
            self.file_path_obj_dst, self.flag_cleaning_dynamic_data)

        if self.flag_cleaning_dynamic_ancillary:
            if not self.flag_cleaning_dynamic_data:
                self.flag_cleaning_dynamic_data = True
                self.file_check_destination = False
                log_stream.warning(' ===> Cleaning ancillary datasets is active. '
                                   'By constants the cleaning of destination datasets will be activated.')

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to check file collections (ancillary or destination)
    def check_file_collections(self, file_path_obj_datasets, flag_cleaning_datasets=True):

        file_check_list = []
        for file_dset_key, file_path_fields in file_path_obj_datasets.items():
            for file_path_obj in file_path_fields.values():
                if (isinstance(file_path_obj, list)) and file_path_obj.__len__() == 1:
                    file_path_obj = file_path_obj[0]
                else:
                    log_stream.error(' ===> File path obj is defined by unsupported format')
                    raise IOError('Case not implemented yet')
                for file_path_step_raw in list(file_path_obj.values()):

                    file_layers_dset = self.parse_var_dict(
                        self.dst_dict[file_dset_key]['file_layer'], obj_list=self.alg_layer_variable)

                    if "layer_name" not in file_path_step_raw:
                        file_layers_tmp = ['']
                    else:
                        file_layers_tmp = deepcopy(file_layers_dset)

                    for file_layer_step in file_layers_tmp:
                        file_path_step_def = fill_tags2string(
                            file_path_step_raw, self.alg_template_data, {'layer_name': file_layer_step})
                        file_path_step_zip = self.define_file_name_zip(file_path_step_def)
                        if os.path.exists(file_path_step_def) or os.path.exists(file_path_step_zip):
                            if flag_cleaning_datasets:
                                if os.path.exists(file_path_step_def):
                                    os.remove(file_path_step_def)
                                    file_check_list.append(False)
                                if os.path.exists(file_path_step_zip):
                                    os.remove(file_path_step_zip)
                                    file_check_list.append(False)
                            else:
                                if os.path.exists(file_path_step_def):
                                    file_check_list.append(True)
                                if os.path.exists(file_path_step_zip):
                                    file_check_list.append(True)
                        else:
                            file_check_list.append(False)

        file_check = all(file_check_list)

        return file_check
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to select geographical reference
    def select_geo_reference(self, geo_dict, ref_dict):

        geo_workspace_tag, geo_workspace_data = None, None
        for geo_key, geo_fields in geo_dict.items():
            if self.file_geo_reference_tag in list(geo_fields.keys()):
                if geo_workspace_tag is None:
                    geo_workspace_tag = {}
                geo_reference = geo_fields[self.file_geo_reference_tag]
                geo_workspace_tag[geo_key] = geo_reference

        if geo_workspace_tag is None:
            log_stream.error(' ===> Geo tag is not found.')
            raise IOError('Check your settings file')

        geo_data = None
        if geo_workspace_tag is not None:
            for geo_key, geo_tag in geo_workspace_tag.items():
                if geo_tag in list(ref_dict.keys()):
                    if geo_data is None:
                        geo_data = {}
                    geo_values = ref_dict[geo_tag]
                    geo_data[geo_key] = geo_values

        if geo_data is None:
            log_stream.error(' ===> Geo datasets is not found.')
            raise IOError('Check your settings file')

        for geo_key, geo_handle in geo_data.items():

            if geo_workspace_data is None:
                geo_workspace_data = {}

            geo_domain = list(geo_handle.items())[0][0]
            geo_handle = list(geo_handle.items())[0][1]

            if os.path.isfile(geo_handle):
                geo_values = read_obj(geo_handle)
                geo_workspace_data[geo_key] = geo_values
            else:
                geo_workspace_data[geo_key] = geo_handle

        return geo_workspace_tag, geo_workspace_data

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set geographical reference
    def set_geo_reference(self, geo_data_workspace, geo_data_tag, geo_key='dataset'):

        geo_ref_collections = geo_data_workspace[geo_key]
        geo_ref_name = geo_data_tag[geo_key]

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
    def set_geo_attributes(dict_info, tag_data='data', tag_geo_x='geo_x', tag_geo_y='geo_y',
                           tag_i_cols_ref='i_cols_ref', tag_j_rows_ref='j_rows_ref',
                           tag_i_cols_dom='i_cols_dom', tag_j_rows_dom='j_rows_dom'):

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

        # Section to get sample method indexes
        i_cols_ref, j_rows_ref, i_cols_dom, j_rows_dom = None, None, None, None
        if tag_i_cols_ref in list(dict_info.keys()):
            i_cols_ref = dict_info[tag_i_cols_ref]
        if tag_j_rows_ref in list(dict_info.keys()):
            j_rows_ref = dict_info[tag_j_rows_ref]
        if tag_i_cols_dom in list(dict_info.keys()):
            i_cols_dom = dict_info[tag_i_cols_dom]
        if tag_j_rows_dom in list(dict_info.keys()):
            j_rows_dom = dict_info[tag_j_rows_dom]

        data_attrs = deepcopy(dict_info)
        [data_attrs.pop(key) for key in [tag_data, tag_geo_x, tag_geo_y]]

        return data_values, data_geo_x, data_geo_y, data_attrs, i_cols_ref, j_rows_ref, i_cols_dom, j_rows_dom
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
    # Method to parse obj dictionary
    def parse_var_dict(self, obj_fields, obj_list=None):

        if obj_list is None:
            obj_list = self.alg_domain_name
        if not isinstance(obj_fields, dict):
            raise IOError('Obj format is not correct')
        obj_flag, obj_value = obj_fields['flag'], obj_fields['value']
        if obj_flag:
            var_data = deepcopy(obj_list)
        else:
            var_data = deepcopy(obj_value)
        if var_data is not None:
            if not isinstance(var_data, list):
                var_data = [var_data]
            if var_data.__len__() == 0:
                var_data = None
        return var_data
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define filename(s) struct
    def define_file_name_struct(self, var_dict, var_list, var_time_period=None, flag_check_domain=False):

        alg_template_data = self.alg_template_data
        alg_template_time = self.alg_template_time

        if not isinstance(var_list, list):
            var_list = [var_list]

        file_workspace = {}
        for var_name in var_list:

            file_collections = {var_name: {}}

            domain_obj = None
            if var_name in list(var_dict.keys()):
                folder_name_step = var_dict[var_name][self.folder_name_tag]
                file_name_step = var_dict[var_name][self.file_name_tag]
                if self.file_domain_tag in list(var_dict[var_name].keys()):
                    domain_obj = var_dict[var_name][self.file_domain_tag]
            else:
                folder_name_step = var_dict[self.folder_name_tag]
                file_name_step = var_dict[self.file_name_tag]
                if self.file_domain_tag in list(var_dict.keys()):
                    domain_obj = var_dict[var_name][self.file_domain_tag]
            domain_list = self.parse_var_dict(domain_obj)

            file_path_step = os.path.join(folder_name_step, file_name_step)

            if var_time_period is not None:
                file_obj = {}
                for time_step in var_time_period:
                    alg_template_step = dict.fromkeys(list(alg_template_time.keys()), time_step)
                    file_obj[time_step] = fill_tags2string(file_path_step, alg_template_time, alg_template_step)
                file_collections[var_name] = deepcopy(file_obj)
            else:
                file_collections[var_name][self.time_reference] = file_path_step

            if domain_list is not None:
                file_obj = {var_name: {}}
                for time_step, file_str_step in file_collections[var_name].items():

                    for domain_step in domain_list:

                        check_domain = True
                        if flag_check_domain:
                            if domain_step not in self.alg_domain_name:
                                check_domain = False

                        if check_domain:

                            alg_template_step = dict.fromkeys(['domain_name'], domain_step)

                            alg_template_intersect = intersect_dicts(alg_template_data, alg_template_step)
                            file_str_filled = fill_tags2string(file_str_step, alg_template_intersect, alg_template_step)

                            if time_step not in list(file_obj[var_name].keys()):
                                file_obj[var_name][time_step] = {}
                                file_obj[var_name][time_step] = [{domain_step: file_str_filled}]
                            else:
                                file_list_tmp = file_obj[var_name][time_step]
                                if file_str_filled not in file_list_tmp:
                                    file_list_tmp.append({domain_step: file_str_filled})
                                    file_obj[var_name][time_step] = file_list_tmp
                        else:
                            log_stream.warning(' ===> Domain name "' + domain_step + '" is not in the list of domains.')
                file_collections = deepcopy(file_obj)

            file_workspace = {**file_workspace, **file_collections}

        return file_workspace
    # -------------------------------------------------------------------------------------

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

        file_include = var_dict[self.file_include_tag]
        file_compression = var_dict[self.file_compression_tag]
        file_geo_reference = var_dict[self.file_geo_reference_tag]
        file_type = var_dict[self.file_type_tag]
        file_coords = var_dict[self.file_coords_tag]
        file_freq = var_dict[self.file_frequency_tag]

        file_geo_mask = None
        if self.file_geo_mask_tag in list(var_dict.keys()):
            file_geo_mask = var_dict[self.file_geo_mask_tag]

        file_time_steps_expected = 1
        if self.file_time_steps_expected_tag in list(var_dict.keys()):
            file_time_steps_expected = var_dict[self.file_time_steps_expected_tag]

        file_time_steps_ref = 1
        if self.file_time_steps_ref_tag in list(var_dict.keys()):
            file_time_steps_ref = var_dict[self.file_time_steps_ref_tag]

        file_time_steps_flag = self.dim_name_time
        if self.file_time_steps_flag_tag in list(var_dict.keys()):
            file_time_steps_flag = var_dict[self.file_time_steps_flag_tag]

        file_domain = {"flag": True, "value": None}
        if self.file_domain_tag in list(var_dict.keys()):
            file_domain = var_dict[self.file_domain_tag]

        file_layer = {"flag": True, "value": None}
        if self.file_layer_tag in list(var_dict.keys()):
            file_layer = var_dict[self.file_layer_tag]

        return (file_include, file_compression, file_geo_reference, file_geo_mask,
                file_type, file_coords, file_freq,
                file_time_steps_expected, file_time_steps_ref, file_time_steps_flag,
                file_domain, file_layer)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean dynamic tmp
    def clean_dynamic_tmp(self):

        flag_cleaning_tmp = self.flag_cleaning_dynamic_tmp
        file_path_anc = self.file_path_obj_anc

        if flag_cleaning_tmp:

            for file_path_fields in file_path_anc.values():
                for file_path_obj in file_path_fields.values():
                    if (isinstance(file_path_obj, list)) and file_path_obj.__len__() == 1:
                        file_path_obj = file_path_obj[0]
                    else:
                        log_stream.error(' ===> File path obj is defined by unsupported format')
                        raise IOError('Case not implemented yet')
                    for file_path_step in list(file_path_obj.values()):
                        folder_name_step, file_name_step = os.path.split(file_path_step)
                        if os.path.exists(file_path_step):
                            os.remove(file_path_step)

                        folder_name_list = find_folder(folder_name_step)
                        for folder_name_step in folder_name_list:
                            if os.path.exists(folder_name_step):
                                if not any(os.scandir(folder_name_step)):
                                    os.rmdir(folder_name_step)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to dump dynamic data
    def dump_dynamic_data(self):

        time_str = self.time_str
        time_period = self.time_period

        var_list_anc = self.var_name_anc
        var_list_dst = self.var_name_dst

        if var_list_anc.__len__() != var_list_dst.__len__():
            log_stream.error(' ===> Variable ancillary length must be == variable destination length')
            raise NotImplementedError('Case not implemented yet')

        file_layers_name = self.alg_layer_variable
        file_layers_scale_factor = self.alg_layer_scale_factor
        file_layers_no_data = self.alg_layer_no_data

        anc_dict = self.anc_dict
        dst_dict = self.dst_dict

        file_path_obj_anc = self.file_path_obj_anc
        file_path_obj_dst = self.file_path_obj_dst

        geo_da_anc = self.geo_anc_da
        geo_da_dst = self.geo_dst_da

        file_check_destination = self.file_check_destination

        method_mask = self.method_mask_destination
        method_interpolate = self.method_interpolate_destination

        log_stream.info(' ---> Dump dynamic datasets [' + time_str + '] ... ')

        # Check elements availability
        if not file_check_destination:

            for var_name_anc, var_name_dst in zip(var_list_anc, var_list_dst):

                log_stream.info(' ----> Save datasets destination "' + var_name_dst + '" ... ')

                file_include_dst, file_compression_dst, file_geo_reference_dst, file_geo_mask_dst, \
                    file_type_dst, file_coords_dst, file_freq_dst, \
                    file_time_steps_expected_dst, file_time_steps_ref_dst, \
                    file_time_steps_flag_dst,\
                    file_domain_dst, file_layer_dst = self.extract_var_fields(dst_dict[var_name_dst])

                var_dset_layer_dst = self.parse_var_dict(file_layer_dst, obj_list=self.alg_layer_variable)

                file_path_collections_anc = file_path_obj_anc[var_name_anc]
                file_path_collections_dst = file_path_obj_dst[var_name_dst]

                if file_include_dst:

                    for (var_time, var_path_list_anc), var_path_list_dst in zip(
                            file_path_collections_anc.items(), file_path_collections_dst.values()):

                        log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) + '" ... ')

                        if isinstance(var_path_list_anc, list) and (var_path_list_anc.__len__() == 1):
                            var_domain_name_anc = list(var_path_list_anc[0].keys())[0]
                            var_file_path_anc = list(var_path_list_anc[0].values())[0]
                        else:
                            log_stream.error(' ===> Ancillary obj must be list and length == 1')
                            raise NotImplementedError('Case not implemented yet')

                        if isinstance(var_path_list_dst, list) and (var_path_list_dst.__len__() == 1):
                            var_domain_name_dst = list(var_path_list_dst[0].keys())[0]
                            var_file_path_dst = list(var_path_list_dst[0].values())[0]
                        else:
                            log_stream.error(' ===> Destination obj must be list and length == 1')
                            raise NotImplementedError('Case not implemented yet')

                        if os.path.exists(var_file_path_anc):

                            var_dset_anc = read_obj(var_file_path_anc)
                            var_dset_anc = filter_dset_vars(var_dset_anc, var_list=var_dset_layer_dst)

                            if var_dset_anc:

                                # Active (if needed) interpolation method to the variable source data-array
                                active_interp = active_var_interpolate(var_dset_anc.attrs, geo_da_dst.attrs)

                                # Apply the interpolation method to the variable source data-array
                                if active_interp:

                                    log_stream.info(
                                        ' ------> Interpolate from ancillary domain "' + var_domain_name_anc +
                                        '" to destination domain "' + var_domain_name_dst + '" ... ')

                                    if method_interpolate in ['nearest']:
                                        var_dset_dst = apply_var_interpolate(
                                            var_dset_anc, geo_da_dst,
                                            dim_name_geo_x=self.dim_name_geo_x, dim_name_geo_y=self.dim_name_geo_y,
                                            coord_name_geo_x=self.coord_name_geo_x, coord_name_geo_y=self.coord_name_geo_y,
                                            interp_method=method_interpolate)
                                        var_dset_dst.attrs = deepcopy(geo_da_dst.attrs)

                                        log_stream.info(
                                            ' ------> Interpolate from ancillary domain "' + var_domain_name_anc +
                                            '" to destination domain "' + var_domain_name_dst + '" ... DONE')
                                    else:
                                        log_stream.error(' ===> Interpolating method "'
                                                         + method_interpolate + '" is not allowed')
                                        raise NotImplementedError('Case not implemented yet')
                                else:
                                    var_dset_dst = deepcopy(var_dset_anc)

                                # Mask the variable destination data-array
                                geo_nodata = None
                                if 'nodata_value' in list(geo_da_dst.attrs.keys()):
                                    geo_nodata = geo_da_dst.attrs['nodata_value']

                                if geo_nodata is not None:
                                    var_dset_masked = var_dset_dst.where(
                                        (geo_da_dst.values[:, :, np.newaxis] != geo_nodata))
                                else:
                                    var_dset_masked = deepcopy(var_dset_dst)

                            else:
                                var_dset_masked = None
                                log_stream.warning(' ===> Datasets is undefined. Data not found')

                            var_file_dict_dst = {}
                            for file_layers_step in file_layers_name:
                                alg_template_step = {'layer_name': file_layers_step}
                                alg_template_intersect = intersect_dicts(self.alg_template_data, alg_template_step)
                                var_file_path_tmp = fill_tags2string(var_file_path_dst,
                                                                     alg_template_intersect, alg_template_step)
                                if var_file_path_tmp not in list(var_file_dict_dst.keys()):
                                    var_file_dict_dst[file_layers_step] = var_file_path_tmp

                            var_attr_dict_dest = {}
                            for file_layers_step, file_no_data_step, file_scale_factor_step in \
                                    zip(file_layers_name, file_layers_no_data, file_layers_scale_factor):
                                var_attr_dict_dest[file_layers_step] = {}
                                var_attr_dict_dest[file_layers_step]['_FillValue'] = file_no_data_step
                                var_attr_dict_dest[file_layers_step]['scale_factor'] = file_scale_factor_step

                            var_file_list_dst = []
                            for var_file_key, var_file_value in var_file_dict_dst.items():
                                if var_file_key in var_dset_layer_dst:
                                    if var_file_value not in var_file_list_dst:
                                        var_file_list_dst.append(var_file_value)

                            if var_dset_masked:

                                if file_type_dst == 'netcdf':

                                    if var_file_list_dst.__len__() == 1:
                                        var_file_obj_dst = var_file_list_dst[0]
                                    else:
                                        log_stream.error(' ===> File name must be unique')
                                        raise RuntimeError('Remove {layer_name} tag from the filename')

                                    if not isinstance(var_file_obj_dst, str):
                                        log_stream.error(' ===> File name must be a string')
                                        raise RuntimeError('Remove {layer_name} tag from the filename')

                                    # Remove file (unzipped and/or zipped) previously created
                                    if os.path.exists(var_file_obj_dst):
                                        os.remove(var_file_obj_dst)
                                    var_file_obj_zip = self.define_file_name_zip(var_file_obj_dst)
                                    if os.path.exists(var_file_obj_zip):
                                        os.remove(var_file_obj_zip)

                                    var_folder_name_dst, var_file_name_dst = os.path.split(var_file_obj_dst)
                                    make_folder(var_folder_name_dst)

                                    if not var_file_name_dst.endswith('nc'):
                                        log_stream.warning(' ===> File name extension must be "nc".\n'
                                                           'The actual file is "' + var_file_name_dst +
                                                           '" and it will be dumped with an unexpected extension.')

                                    if self.alg_layer_nc_format == 'continuum':
                                        var_dset_remap = create_dset_continuum(
                                            var_time, var_dset_masked, geo_da_dst.values,
                                            geo_da_dst['longitude'].values, geo_da_dst['latitude'].values,
                                            geo_da_dst.attrs, var_data_attrs=var_attr_dict_dest)
                                    elif self.alg_layer_nc_format is None:
                                        var_dset_remap = deepcopy(var_dset_masked)
                                    else:
                                        log_stream.error(
                                            ' ===> Remap type "' + str(self.alg_layer_nc_format) +
                                            '" is not permitted. Only "continuum" or NoneType flag are activated')
                                        raise NotImplementedError('Case not implemented yet')

                                    '''
                                    # DEBUG
                                    plt.figure()
                                    plt.imshow(var_dset_dst['SM'].values[:, :, 0])
                                    plt.colorbar()
                                    plt.figure()
                                    plt.imshow(var_dset_masked['SM'].values[:, :, 0])
                                    plt.colorbar()
                                    plt.figure()
                                    plt.imshow(var_dset_remap['SM'].values)
                                    plt.colorbar()
                                    
                                    plt.figure()
                                    plt.imshow(var_dset_remap['TQ'].values[:, :, 0])
                                    plt.colorbar()
                                    plt.figure()
                                    plt.imshow(var_dset_remap['terrain'].values)
                                    plt.colorbar()
                                    
                                    plt.show()
                                    '''

                                    log_stream.info(' ------> Save datasets "' + var_file_name_dst + '" ... ')
                                    write_dset_nc(var_file_obj_dst, var_dset_remap,
                                                  dset_engine=self.nc_type_engine, dset_format=self.nc_type_file,
                                                  dset_compression=self.nc_compression_level, fill_data=-9999.0,
                                                  dset_type='float32')
                                    log_stream.info(' ------> Save datasets "' + var_file_name_dst + '" ... DONE ')

                                elif file_type_dst == 'tiff' or file_type_dst == 'tif':

                                    log_stream.info(' ------> Save datasets group  ... ')

                                    var_file_obj_dst = deepcopy(var_file_dict_dst)

                                    if not isinstance(var_file_obj_dst, dict):
                                        log_stream.error(' ===> File name must be a dictionary {var_name: file_name}')
                                        raise RuntimeError('Check your settings to pass the correct file template.')

                                    var_file_name_list = []
                                    for var_name, var_file_path_dst in var_file_obj_dst.items():

                                        var_folder_name_dst, var_file_name_dst = os.path.split(var_file_path_dst)
                                        make_folder(var_folder_name_dst)

                                        if (not var_file_name_dst.endswith('tiff')) and (
                                                not var_file_name_dst.endswith('tif')):
                                            log_stream.warning(' ===> File name extension must be "tiff" or "tif".\n'
                                                               'The actual file is "' + var_file_name_dst +
                                                               '" and it will be dumped with an unexpected extension.')

                                        if var_file_name_dst not in var_file_name_list:
                                            var_file_name_list.append(var_file_name_dst)
                                        else:
                                            log_stream.error(
                                                ' ===> File name must be different for each variable considered')
                                            raise RuntimeError('Insert {layer_name} tag in the filename')

                                    '''
                                    # DEBUG
                                    var_values = var_dset_masked['SM'].values
                                    plt.figure()
                                    plt.imshow(var_values[:,:,0])
                                    plt.colorbar()
                                    '''

                                    write_dset_tiff(var_file_obj_dst, var_dset_masked,
                                                    file_compression_option=self.tiff_compression_option)

                                    log_stream.info(' ------> Save datasets group  ... DONE')

                                else:
                                    log_stream.error(' ===> File format for saving datasets is not implemented ')
                                    raise NotImplementedError('Case not implemented yet')

                                for var_file_step_dst in var_file_list_dst:

                                    var_folder_name_dst, var_file_name_dst = os.path.split(var_file_step_dst)

                                    log_stream.info(' ------> Zip datasets "' + var_file_name_dst + '" ... ')
                                    if file_compression_dst:
                                        if os.path.exists(var_file_step_dst):

                                            var_file_step_zip = self.define_file_name_zip(var_file_step_dst)
                                            zip_filename(var_file_step_dst, var_file_step_zip)

                                            if os.path.exists(var_file_step_dst) and (var_file_step_zip != var_file_step_dst):
                                                os.remove(var_file_step_dst)

                                            log_stream.info(' ------> Zip datasets "' + var_file_name_dst +
                                                            '" ... DONE')
                                        else:
                                            log_stream.info(' ------> Zip datasets "' + var_file_name_dst +
                                                            '" ... SKIPPED. File does not exist.')
                                    else:
                                        log_stream.info(' ------> Zip datasets "' + var_file_name_dst +
                                                        '" ... SKIPPED. Compression is not activated.')

                                log_stream.info(
                                    ' -----> Time "' + var_time.strftime(time_format_algorithm) + '" ... DONE')
                            else:
                                log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                                '" ... SKIPPED. Datasets destination is not defined')
                        else:
                            log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                            '" ... SKIPPED. Datasets ancillary is not defined')

                    log_stream.info(' ----> Save datasets destination "' + var_name_dst + '" ... DONE')

                else:
                    log_stream.info(' ----> Save datasets destination "' + var_name_dst +
                                    '" ... SKIPPED. Compute flag not activated.')

            log_stream.info(' ---> Dump dynamic datasets [' + time_str + '] ... DONE')
        else:
            log_stream.info(' ---> Dump dynamic datasets [' +
                            time_str + '] ... SKIPPED. All destination datasets are previously saved')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to merge dynamic data
    def organize_dynamic_data(self):

        time_str = self.time_str

        src_dict = self.src_dict
        anc_dict = self.anc_dict

        geo_da_anc = self.geo_anc_da

        file_path_obj_src = self.file_path_obj_src
        file_path_obj_anc = self.file_path_obj_anc

        var_list_src = self.var_name_src
        var_list_anc = self.var_name_anc
        if var_list_src.__len__() > var_list_anc.__len__():
            var_list_tmp = var_list_anc * var_list_src.__len__()
        elif var_list_src.__len__() == var_list_anc.__len__():
            var_list_tmp = deepcopy(var_list_anc)
        else:
            log_stream.error(' ===> Variable source length must be >= variable ancillary length')
            raise NotImplementedError('Case not implemented yet')

        file_layers_name = self.alg_layer_variable
        file_layers_scale_factor = self.alg_layer_scale_factor
        file_layers_no_data = self.alg_layer_no_data

        file_check_ancillary = self.file_check_ancillary
        file_check_destination = self.file_check_destination

        method_mask = self.method_mask_source
        method_interpolate = self.method_interpolate_source

        log_stream.info(' ---> Organize dynamic datasets [' + time_str + '] ... ')

        # Check elements availability
        if not file_check_destination:

            if not file_check_ancillary:

                dset_collection_tmp = None
                for var_name_src, var_name_tmp in zip(var_list_src, var_list_tmp):

                    log_stream.info(' ----> Get datasets source "' + var_name_src + '" ... ')

                    file_include_src, file_compression_src, file_geo_reference_src, file_geo_mask_src, \
                        file_type_src, file_coords_src, file_freq_src, \
                        file_time_steps_expected_src, file_time_steps_ref_src, \
                        file_time_steps_flag_src,\
                        file_domain_src, file_layer_src = self.extract_var_fields(src_dict[var_name_src])

                    var_dset_layer_src = self.parse_var_dict(file_layer_src, obj_list=self.alg_layer_variable)

                    file_path_collections_src = file_path_obj_src[var_name_src]

                    if file_include_src:

                        for var_time, var_path_list_src in file_path_collections_src.items():

                            log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) + '" ... ')

                            for var_path_fields_step in var_path_list_src:

                                # DEBUG
                                # var_path_fields_step = var_path_list_src[12]

                                var_domain_name_src = list(var_path_fields_step.keys())[0]
                                var_file_path_src = list(var_path_fields_step.values())[0]

                                log_stream.info(' ------> Domain "' + var_domain_name_src + '" ... ')

                                geo_file_obj = None
                                if file_geo_reference_src is not None:
                                    if file_geo_reference_src in list(self.static_data_src.keys()):
                                        geo_file_obj = self.static_data_src[file_geo_reference_src]
                                    else:
                                        log_stream.error(' ===> Geographical info must be defined in the static object')
                                        raise RuntimeError('Algorithm will produce unexpected errors.')
                                else:
                                    log_stream.error(' ===> Geographical info is defined by NoneType object')
                                    raise RuntimeError('Algorithm will produce unexpected errors.')

                                mask_file_obj = None
                                if file_geo_mask_src is not None:
                                    if file_geo_mask_src in list(self.static_data_src.keys()):
                                        mask_file_obj = self.static_data_src[file_geo_mask_src]

                                if method_mask is not None:
                                    if mask_file_obj is None:
                                        log_stream.warning(' ===> Mask info is defined by NoneType object')

                                if var_domain_name_src in list(geo_file_obj.keys()):
                                    geo_file_name = geo_file_obj[var_domain_name_src]
                                    if os.path.exists(geo_file_name):
                                        geo_file_data = read_obj(geo_file_name)
                                        geo_file_values, geo_file_x, geo_file_y, geo_file_attrs,\
                                            i_cols_ref, j_rows_ref, i_cols_dom, j_rows_dom = \
                                            self.set_geo_attributes(geo_file_data)
                                    else:
                                        log_stream.error(' ===> Geographical datasets "' + geo_file_name + '" not found')
                                        raise IOError('Geographical datasets not available. Check your settings file')
                                else:
                                    log_stream.error(' ===> Geographical domain "' + var_domain_name_src + '" not found')
                                    raise IOError('Geographical domain not available. Check your settings file')

                                mask_file_data, mask_file_values = None, None
                                mask_file_x, mask_file_y, mask_file_attrs = None, None, None
                                if mask_file_obj is not None:
                                    if var_domain_name_src in list(mask_file_obj.keys()):
                                        mask_file_name = mask_file_obj[var_domain_name_src]
                                        if os.path.exists(mask_file_name):
                                            mask_file_data = read_obj(mask_file_name)
                                            mask_file_values, mask_file_x, mask_file_y, mask_file_attrs, _, _, _, _ = \
                                                self.set_geo_attributes(mask_file_data)
                                        else:
                                            log_stream.warning(' ===> Mask datasets "' + mask_file_name + '" not found')
                                    else:
                                        log_stream.warning(' ===> Mask domain "' + var_domain_name_src + '" not found')

                                if os.path.exists(var_file_path_src):

                                    if dset_collection_tmp is None:
                                        dset_collection_tmp = {}
                                    if var_name_tmp not in list(dset_collection_tmp.keys()):
                                        dset_collection_tmp[var_name_tmp] = {}

                                    if file_compression_src:
                                        var_file_path_tmp = self.define_file_name_unzip(var_file_path_src)
                                        unzip_filename(var_file_path_src, var_file_path_tmp)
                                    else:
                                        var_file_path_tmp = deepcopy(var_file_path_src)

                                    if file_type_src == 'netcdf':

                                        var_dset_src = read_data_nc(
                                            var_file_path_tmp, geo_file_x, geo_file_y, geo_file_attrs,
                                            var_coords=file_coords_src,
                                            var_scale_factor=file_layers_scale_factor, var_name=file_layers_name,
                                            var_no_data=file_layers_no_data,
                                            var_time=var_time,
                                            coord_name_geo_x=self.coord_name_geo_x,
                                            coord_name_geo_y=self.coord_name_geo_y,
                                            coord_name_time=self.coord_name_time,
                                            dim_name_geo_x=self.dim_name_geo_x,
                                            dim_name_geo_y=self.dim_name_geo_y,
                                            dim_name_time=self.dim_name_time,
                                            dims_order=self.dims_order_3d)

                                        var_dset_src = filter_dset_vars(var_dset_src, var_list=var_dset_layer_src)

                                    elif file_type_src == 'tif' or file_type_src == 'tiff':

                                        var_dset_src = read_data_tiff(
                                            var_file_path_tmp,
                                            var_scale_factor=file_layers_scale_factor, var_type='float32',
                                            var_name=file_layers_name,
                                            var_time=var_time, var_no_data=file_layers_no_data,
                                            coord_name_geo_x=self.coord_name_geo_x,
                                            coord_name_geo_y=self.coord_name_geo_y,
                                            coord_name_time=self.coord_name_time,
                                            dim_name_geo_x=self.dim_name_geo_x,
                                            dim_name_geo_y=self.dim_name_geo_y,
                                            dim_name_time=self.dim_name_time,
                                            dims_order=self.dims_order_3d,
                                            decimal_round_data=7, flag_round_data=False,
                                            decimal_round_geo=7, flag_round_geo=True,
                                            flag_obj_type='Dataset')

                                        var_dset_src = filter_dset_vars(var_dset_src, var_list=None)

                                    else:
                                        log_stream.error(' ===> File type "' + file_type_src + '"is not allowed.')
                                        raise NotImplementedError('Case not implemented yet')

                                    # Delete (if needed the uncompressed file(s)
                                    if var_file_path_src != var_file_path_tmp:
                                        if os.path.exists(var_file_path_tmp):
                                            os.remove(var_file_path_tmp)

                                    # Organize destination dataset
                                    if var_dset_src is not None:

                                        # Active (if needed) mask method to the variable source data-array
                                        active_mask = False
                                        if method_mask is not None and mask_file_obj is not None:
                                            active_mask = active_var_mask(var_dset_src.attrs, mask_file_attrs)

                                        # Active (if needed) interpolation method to the variable source data-array
                                        active_interp = active_var_interpolate(var_dset_src.attrs, self.geo_anc_da.attrs)

                                        '''
                                        # DEBUG
                                        plt.figure()
                                        plt.imshow(var_dset_src['SM'].values[:, :, 0])
                                        plt.colorbar()
                                        plt.figure()
                                        plt.imshow(var_dset_src['LST'].values[:, :, 0])
                                        plt.colorbar()
                                        plt.show()
                                        '''

                                        if active_mask:
                                            if method_mask == 'watermark':
                                                var_dset_src = apply_var_mask(var_dset_src, mask_file_values)
                                            else:
                                                log_stream.error(' ===> Masking method "'
                                                                 + method_mask + '" is not allowed')
                                                raise NotImplementedError('Case not implemented yet')

                                        # Apply the interpolation method to the variable source data-array
                                        if active_interp:
                                            if method_interpolate in ['nearest', 'linear']:
                                                var_dset_anc = apply_var_interpolate(
                                                    var_dset_src, geo_da_anc,
                                                    dim_name_geo_x=self.dim_name_geo_x, dim_name_geo_y=self.dim_name_geo_y,
                                                    coord_name_geo_x=self.coord_name_geo_x, coord_name_geo_y=self.coord_name_geo_y,
                                                    interp_method=method_interpolate)
                                            elif method_interpolate == 'sample':
                                                var_dset_anc = apply_var_sample(
                                                    var_dset_src, geo_da_anc,
                                                    i_cols_ref, j_rows_ref, i_cols_dom, j_rows_dom)
                                            else:
                                                log_stream.error(' ===> Interpolating method "'
                                                                 + method_interpolate + '" is not allowed')
                                                raise NotImplementedError('Case not implemented yet')
                                        else:
                                            var_dset_anc = deepcopy(var_dset_src)

                                        '''
                                        # DEBUG
                                        plt.figure()
                                        plt.imshow(var_dset_anc['SM'].values[:, :, 0])
                                        plt.colorbar()
                                        plt.figure()
                                        plt.imshow(var_dset_anc['LST'].values[:, :, 0])
                                        plt.colorbar()
                                        plt.show()
                                        '''

                                        # Mask the variable destination data-array
                                        var_nodata = None
                                        if 'nodata_value' in list(var_dset_anc.attrs.keys()):
                                            var_nodata = var_dset_anc.attrs['nodata_value']
                                        geo_nodata = None
                                        if 'nodata_value' in list(geo_da_anc.attrs.keys()):
                                            geo_nodata = geo_da_anc.attrs['nodata_value']

                                        if geo_nodata is not None and (var_nodata is not None):
                                            var_dset_masked = var_dset_anc.where(
                                                ((geo_da_anc.values[:, :, np.newaxis] != geo_nodata) != geo_nodata) &
                                                (var_dset_anc != var_nodata))
                                        else:
                                            var_dset_masked = deepcopy(var_dset_anc)

                                        if var_time not in list(dset_collection_tmp[var_name_tmp].keys()):
                                            dset_collection_tmp[var_name_tmp][var_time] = var_dset_masked
                                        elif var_time in list(dset_collection_tmp[var_name_tmp].keys()):
                                            var_dset_tmp = dset_collection_tmp[var_name_tmp][var_time]
                                            attrs_dset_tmp = var_dset_tmp.attrs

                                            var_dset_tmp_adj, var_dset_masked_adj = adjust_dset_vars(
                                                var_dset_tmp, var_dset_masked)

                                            # Iterate over variables to aggregate layers
                                            for file_layer_name, file_layer_no_data in zip(
                                                    file_layers_name, file_layers_no_data):

                                                if (file_layer_name in list(var_dset_masked_adj.variables)) and \
                                                        (file_layer_name in list(var_dset_masked_adj.variables)):

                                                    var_da_masked_adj = var_dset_masked_adj[file_layer_name]
                                                    var_da_tmp_adj = var_dset_tmp_adj[file_layer_name].reindex_like(var_da_masked_adj)    ###MODIFIED

                                                    var_da_filled_adj = xr.where(
                                                        (var_da_tmp_adj != file_layer_no_data)
                                                        & (np.isfinite(var_da_masked_adj)),
                                                        var_da_masked_adj, var_da_tmp_adj)

                                                    var_dset_masked_adj[file_layer_name] = deepcopy(var_da_filled_adj)

                                            var_dset_merged = deepcopy(var_dset_masked_adj)

                                            var_dset_merged.attrs = attrs_dset_tmp
                                            dset_collection_tmp[var_name_tmp][var_time] = var_dset_merged

                                        '''
                                        # DEBUG
                                        plt.figure()
                                        plt.imshow(var_dset_src['SM'].values[:, :, 0])
                                        plt.colorbar()
                                        plt.figure()
                                        plt.imshow(var_dset_masked['SM'].values[:, :, 0])
                                        plt.colorbar()
                                        plt.figure()
                                        plt.imshow(dset_collection_tmp[var_name_tmp][var_time]['SM'].values[:, :, 0])
                                        plt.colorbar()
                                        plt.show()
                                        print()
                                        '''

                                    else:
                                        log_stream.warning(' ===> Datasets is undefined. Data not found')
                                else:
                                    log_stream.warning(' ===> File "' + var_file_path_src +
                                                       '" is not available. Data not found')

                                log_stream.info(' ------> Domain "' + var_domain_name_src + '" ... DONE')

                            log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) + '" ... DONE')

                        log_stream.info(' ----> Get datasets source "' + var_name_src + '" ... DONE')

                    else:
                        log_stream.info(' ----> Get datasets source  "' + var_name_src +
                                        '" ... SKIPPED. Compute flag not activated.')

                for var_name_anc in var_list_anc:

                    log_stream.info(' ----> Save datasets ancillary "' + var_name_anc + '" ... ')

                    if (dset_collection_tmp is not None) and (var_name_anc in list(dset_collection_tmp.keys())):

                        file_include_anc, file_compression_anc, file_geo_reference_anc, file_geo_mask_anc, \
                            file_type_anc, file_coords_anc, file_freq_anc, \
                            file_time_steps_expected_anc, file_time_steps_ref_anc, \
                            file_time_steps_flag_anc, \
                            file_domain_anc, file_layer_anc = self.extract_var_fields(anc_dict[var_name_anc])

                        var_dset_layer_anc = self.parse_var_dict(file_layer_anc, obj_list=self.alg_layer_variable)

                        file_path_collections_anc = file_path_obj_anc[var_name_anc]

                        if file_compression_anc is not None:
                            log_stream.warning(
                                ' ===> Compression flag is not available for ancillary datasets by constants')
                        if file_type_anc != 'pickle':
                            log_stream.error(
                                ' ===> Only "pickle" format is supported for ancillary datasets by constants ')
                            raise NotImplementedError('Case not implemented yet')

                        for var_time, var_path_list_anc in file_path_collections_anc.items():

                            log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) + '" ... ')

                            if isinstance(var_path_list_anc, list) and (var_path_list_anc.__len__() == 1):
                                var_domain_name_anc = list(var_path_list_anc[0].keys())[0]
                                var_file_path_anc = list(var_path_list_anc[0].values())[0]
                            else:
                                log_stream.error(' ===> Ancillary obj must be list and length == 1')
                                raise NotImplementedError('Case not implemented yet')

                            if not os.path.exists(var_file_path_anc):
                                var_folder_name_anc, var_file_name_anc = os.path.split(var_file_path_anc)
                                make_folder(var_folder_name_anc)

                                if var_time in list(dset_collection_tmp[var_name_anc].keys()):

                                    log_stream.info(' ------> Domain "' + var_domain_name_anc + '" ... ')
                                    dset_collection_anc = dset_collection_tmp[var_name_anc][var_time]

                                    dset_collection_anc = filter_dset_vars(
                                        dset_collection_anc, var_list=var_dset_layer_anc)

                                    write_obj(var_file_path_anc, dset_collection_anc)
                                    log_stream.info(' ------> Domain "' + var_domain_name_anc + '" ... DONE')

                                    log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                                    '" ... DONE')
                                else:
                                    log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                                    '" ... SKIPPED. Datasets not available')
                            else:
                                log_stream.info(' -----> Time "' + var_time.strftime(time_format_algorithm) +
                                                '" ... SKIPPED. Datasets previously savec')

                        log_stream.info(' ----> Save datasets ancillary "' + var_name_anc + '" ... DONE')

                    else:
                        log_stream.info(' ----> Save datasets ancillary "' + var_name_anc +
                                        '" ... SKIPPED. Datasets is null')

                log_stream.info(' ---> Organize dynamic datasets [' + time_str + '] ... DONE')
            else:
                log_stream.info(' ---> Organize dynamic datasets [' +
                                time_str + '] ... SKIPPED. All ancillary datasets are previously computed')
        else:
            log_stream.info(' ---> Organize dynamic datasets [' +
                            time_str + '] ... SKIPPED. All destination datasets are previously computed')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
