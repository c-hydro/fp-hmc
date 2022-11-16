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
import numpy as np

from copy import deepcopy

from tools.processing_tool_datasets_merger.lib_data_io_nc import read_data_nc
from tools.processing_tool_datasets_merger.lib_data_io_tiff import read_data_tiff
from tools.processing_tool_datasets_merger.lib_data_io_ascii import read_data_grid, create_data_grid
from tools.processing_tool_datasets_merger.lib_data_io_generic import parse_data_grid, extract_data_grid

from tools.processing_tool_datasets_merger.lib_utils_io import read_obj, write_obj
from tools.processing_tool_datasets_merger.lib_utils_system import fill_tags2string, make_folder
from tools.processing_tool_datasets_merger.lib_utils_gzip import unzip_filename
from tools.processing_tool_datasets_merger.lib_utils_geo import create_idx_partial2global

from tools.processing_tool_datasets_merger.lib_info_args import logger_name, zip_extension

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverStatic
class DriverStatic:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, src_dict, anc_dict=None, dst_dict=None,
                 alg_ancillary=None, alg_template=None,
                 flag_file_data='file_obj', flag_grid_data='grid_obj',
                 flag_dset_source='source', flag_dset_ancillary='ancillary', flag_dset_destination='destination',
                 flag_dset_cleaning=True):

        self.flag_file_data = flag_file_data
        self.flag_grid_data = flag_grid_data

        self.flag_dset_source = flag_dset_source
        self.flag_dset_ancillary = flag_dset_ancillary
        self.flag_dset_destination = flag_dset_destination

        self.alg_template_data = alg_template['data']
        self.alg_template_time = alg_template['time']

        self.file_layer_tag = 'file_layer'
        self.file_domain_tag = 'file_domain'
        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'
        self.file_compression_tag = 'file_compression'
        self.file_type_tag = 'file_type'
        self.file_coords_tag = 'file_coords'

        self.file_obj_fields = [self.file_name_tag, self.folder_name_tag]
        self.grid_obj_fields = ["xll_corner", "yll_corner", "cell_size", "rows", "cols"]

        self.src_obj = self.define_collection_obj(src_dict)
        self.anc_obj = self.define_collection_obj(anc_dict)
        self.dst_obj = self.define_collection_obj(dst_dict)

        self.domain_name_tag = 'domain_name'

        domain_name = alg_ancillary[self.domain_name_tag]
        if not isinstance(domain_name, list):
            domain_name = [domain_name]
        self.domain_name = domain_name

        self.method_interpolate_source = 'nearest'
        if 'layer_method_interpolate_source' in list(alg_ancillary.keys()):
            self.method_interpolate_source = alg_ancillary['layer_method_interpolate_source']

        self.method_mask_source = None
        if 'layer_method_mask_source' in list(alg_ancillary.keys()):
            self.method_mask_source = alg_ancillary['layer_method_mask_source']

        if self.method_mask_source is not None:
            if 'watermark_dataset' not in list(src_dict.keys()):
                log_stream.error(' ===> "WaterMark" source file must be defined if "WaterMark masking" is activated')
                raise RuntimeError('Check your settings and set the "watermark_dataset" in source files')
            if 'watermark_dataset' not in list(anc_dict.keys()):
                log_stream.error(' ===> "WaterMark" ancillary file must be defined if "WaterMark masking" is activated')
                raise RuntimeError('Check your settings and set the "watermark_dataset" in ancillary files')

        self.flag_dset_cleaning = flag_dset_cleaning

        self.coord_x_default = 'longitude'
        self.coord_y_default = 'latitude'
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to check collection field
    @staticmethod
    def check_collections_field(field_name, field_obj, field_value_default=None):
        field_value_def = deepcopy(field_value_default)
        if field_name in list(field_obj.keys()):
            field_value_def = field_obj[field_name]
        return field_value_def
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define collection obj
    def define_collection_obj(self, obj_dict_in):
        obj_dict_out = {}
        for obj_key, obj_fields in obj_dict_in.items():

            if all(key in list(obj_fields.keys()) for key in self.file_obj_fields):

                # file data case
                obj_folder_name = obj_fields[self.folder_name_tag]
                obj_file_name = obj_fields[self.file_name_tag]
                obj_file_path = os.path.join(obj_folder_name, obj_file_name)

                file_compression = self.check_collections_field(
                    self.file_compression_tag, obj_fields, field_value_default=False)
                file_type = self.check_collections_field(
                    self.file_type_tag, obj_fields, field_value_default=None)
                file_layer = self.check_collections_field(
                    self.file_layer_tag, obj_fields, field_value_default=None)
                file_coords = self.check_collections_field(
                    self.file_coords_tag, obj_fields, field_value_default=None)
                file_domain = self.check_collections_field(
                    self.file_domain_tag, obj_fields, field_value_default={"flag": False, "value": None})

                obj_collections = self.zip_var_fields(
                    obj_file_path, self.flag_file_data,
                    obj_compression=file_compression, obj_type=file_type,
                    obj_layer=file_layer,
                    obj_coords=file_coords, obj_domain=file_domain)

            elif all(key in list(obj_fields.keys()) for key in self.grid_obj_fields):

                # grid data case
                obj_collections = self.zip_var_fields(
                    obj_fields, self.flag_grid_data,
                    obj_compression=False, obj_type=None,
                    obj_layer=None, obj_coords=None, obj_domain=None)
            else:
                log_stream.error(' ===> Static key "' + obj_key + '" is not in allowed format')
                raise NotImplementedError('Case not implemented yet')

            obj_dict_out[obj_key] = obj_collections

        return obj_dict_out
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
    # Method to zip variable field(s)
    @staticmethod
    def zip_var_fields(obj_source, obj_format, obj_compression=False, obj_type=None,
                       obj_layer=None, obj_coords=None,
                       obj_domain=None):

        if obj_domain is None:
            obj_domain = {"flag": False, "value": None}
        obj_collections = {'source': obj_source, 'format': obj_format,
                           'compression': obj_compression, 'type': obj_type,
                           'layer': obj_layer, 'coords': obj_coords,
                           'domain': obj_domain}

        return obj_collections
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to extract variable field(s)
    @staticmethod
    def extract_geo_fields(obj_collections):
        obj_x, obj_y = None, None
        obj_yllcorner, obj_xllcorner, obj_cellsize = None, None, None
        if obj_collections is not None:
            obj_x = obj_collections['geo_x']
            obj_y = obj_collections['geo_y']
            obj_yllcorner = obj_collections['yllcorner']
            obj_xllcorner = obj_collections['xllcorner']
            obj_cellsize = obj_collections['cellsize']
        return obj_x, obj_y, obj_xllcorner, obj_yllcorner, obj_cellsize
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to extract variable field(s)
    @staticmethod
    def extract_var_fields(obj_collections):

        obj_source, obj_format = None, None
        obj_compression, obj_type = None, None
        obj_variable, obj_x, obj_y = None, None, None
        obj_coords, obj_domain, obj_layer = None, None, None
        if obj_collections is not None:
            obj_source = obj_collections['source']
            obj_format = obj_collections['format']
            obj_compression = obj_collections['compression']
            obj_type = obj_collections['type']
            obj_layer = obj_collections['layer']

            obj_coords = None
            if 'coords' in list(obj_collections.keys()):
                obj_coords = obj_collections['coords']

            obj_domain = obj_collections['domain']

        return obj_source, obj_format, obj_compression,  obj_type,  obj_layer, obj_coords, obj_domain
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to parse obj domain
    def parse_var_domain(self, obj_domain):
        if not isinstance(obj_domain, dict):
            raise IOError('Obj format is not correct')
        obj_flag, obj_value = obj_domain['flag'], obj_domain['value']
        if obj_flag:
            var_domain = deepcopy(self.domain_name)
        else:
            var_domain = deepcopy(obj_value)
        if var_domain is not None:
            if not isinstance(var_domain, list):
                var_domain = [var_domain]
            if var_domain.__len__() == 0:
                var_domain = None
        return var_domain
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get collections fields
    def get_collections_fields(self, obj_ref, obj_anc):

        obj_collections_fields = {}
        for obj_key, obj_collections_ref in obj_ref.items():

            # Info start
            log_stream.info(' ----> Get "' + obj_key + '" datasets ... ')

            if obj_collections_ref['format'] in ['file_obj', 'grid_obj']:
                obj_data_ref_raw, obj_format_ref, obj_compression_ref, \
                    obj_type_ref, obj_layer_ref,  \
                    obj_coords_ref, obj_domain_ref = self.extract_var_fields(obj_collections_ref)
            else:
                log_stream.error(' ===> Source format for variable "' + obj_key + '" is badly defined.')
                raise IOError('Only "file_obj" and "grid_obj" are allowed as flag format')

            if obj_data_ref_raw is None:
                log_stream.error(' ===> Source datasets for variable "' + obj_key + '" is not defined.')
                raise IOError('Both source and ancillary "folder_name" and "file_name" are needed by the procedure')

            domain_list_ref = self.parse_var_domain(obj_domain_ref)

            if obj_key in list(obj_anc.keys()):
                obj_collections_anc = obj_anc[obj_key]
            else:
                obj_collections_anc = None
            obj_data_anc_raw, obj_format_anc, obj_compression_anc, \
                obj_type_anc, obj_layer_anc, \
                obj_coords_anc, obj_domain_anc = self.extract_var_fields(obj_collections_anc)

            if obj_data_anc_raw is None:
                log_stream.error(' ===> Ancillary datasets for variable "' + obj_key + '" is not defined.')
                raise IOError('Both source and ancillary "folder_name" and "file_name" are needed by the procedure')

            alg_data_ref_obj, alg_data_anc_obj = {}, {}
            if domain_list_ref is not None:
                for domain_step in domain_list_ref:
                    alg_template_step = {self.domain_name_tag: domain_step}

                    obj_data_ref_def = fill_tags2string(
                        obj_data_ref_raw, self.alg_template_data, alg_template_step)
                    alg_data_ref_obj[domain_step] = obj_data_ref_def

                    obj_data_anc_def = fill_tags2string(
                        obj_data_anc_raw, self.alg_template_data, alg_template_step)

                    alg_data_anc_obj[domain_step] = obj_data_anc_def
            else:
                alg_data_ref_obj['data'] = deepcopy(obj_data_ref_raw)
                alg_data_anc_obj['data'] = deepcopy(obj_data_anc_raw)

            if obj_key not in list(obj_collections_fields.keys()):
                obj_collections_fields[obj_key] = {}

            for (data_key, data_ref), data_anc in zip(
                    alg_data_ref_obj.items(), alg_data_anc_obj.values()):

                if data_key not in list(obj_collections_fields[obj_key].keys()):
                    obj_collections_fields[obj_key][data_key] = {}

                file_path_anc = deepcopy(data_anc)

                if self.flag_dset_cleaning:
                    if os.path.exists(file_path_anc):
                        os.remove(file_path_anc)

                if not os.path.exists(file_path_anc):
                    if obj_format_ref == self.flag_file_data:

                        file_path_ref = deepcopy(data_ref)

                        if obj_compression_ref:
                            file_path_tmp = self.define_file_name_unzip(file_path_ref)
                            unzip_filename(file_path_ref, file_path_tmp)
                        else:
                            file_path_tmp = deepcopy(file_path_ref)

                        if obj_type_ref == 'ascii':
                            obj_data_tmp = read_data_grid(file_path_tmp, output_format='dictionary')

                            if obj_data_tmp is not None:

                                obj_data_grid = extract_data_grid(obj_data_tmp['values'],
                                                                  obj_data_tmp['longitude'], obj_data_tmp['latitude'],
                                                                  obj_data_tmp['transform'], obj_data_tmp['bbox'])

                            else:
                                log_stream.warning(' ===> The obj "obj_data_grid" will be defined by NoneType')
                                obj_data_grid = None

                        elif obj_type_ref == 'netcdf':

                            obj_dims_ref = [obj_coords_ref['y'], obj_coords_ref['x']]
                            obj_data_tmp = read_data_nc(file_path_tmp, var_coords=obj_coords_ref,
                                                        dims_order=obj_dims_ref,
                                                        dim_name_geo_x=obj_coords_ref['x'],
                                                        dim_name_geo_y=obj_coords_ref['y'],
                                                        var_name=obj_layer_ref)

                            if obj_data_tmp is not None:
                                obj_values, obj_geo_x, obj_geo_y, obj_geo_transform = parse_data_grid(obj_data_tmp)
                                obj_data_grid = extract_data_grid(obj_values, obj_geo_x, obj_geo_y, obj_geo_transform)
                            else:
                                log_stream.warning(' ===> The obj "obj_data_grid" will be defined by NoneType')
                                obj_data_grid = None

                        elif obj_type_ref == 'tiff':

                            if obj_coords_ref['y'] is None:
                                obj_coords_ref['y'] = self.coord_y_default
                            if obj_coords_ref['x'] is None:
                                obj_coords_ref['x'] = self.coord_x_default

                            obj_dims_ref = [obj_coords_ref['y'], obj_coords_ref['x']]
                            obj_data_tmp = read_data_tiff(file_path_tmp,
                                                          dim_name_geo_x=obj_coords_ref['x'],
                                                          dim_name_geo_y=obj_coords_ref['y'],
                                                          dims_order=obj_dims_ref)
                            if obj_data_tmp is not None:
                                obj_values, obj_geo_x, obj_geo_y, obj_geo_transform = parse_data_grid(obj_data_tmp)
                                obj_data_grid = extract_data_grid(obj_values, obj_geo_x, obj_geo_y, obj_geo_transform)
                            else:
                                log_stream.warning(' ===> The obj "obj_data_grid" will be defined by NoneType')
                                obj_data_grid = None

                        else:
                            log_stream.error(' ===> Static type "' + obj_type_ref + '" is not allowed')
                            raise NotImplementedError('Case not implemented yet')

                    elif obj_format_ref == self.flag_grid_data:
                        obj_data_fields = deepcopy(data_ref)
                        obj_data_grid = create_data_grid(obj_data_fields)
                    else:
                        log_stream.error(' ===> Static obj "' + str(obj_format_ref) + '" is not allowed')
                        raise NotImplementedError('Case not implemented yet')

                    if file_path_anc is not None:

                        folder_name_anc, file_name_anc = os.path.split(file_path_anc)
                        if obj_data_grid is not None:

                            make_folder(folder_name_anc)
                            write_obj(file_path_anc, obj_data_grid)

                            obj_collections_fields[obj_key][data_key] = file_path_anc
                        else:
                            log_stream.warning(' ===> The ancillary file "' + file_name_anc +
                                               '" is not saved because the related obj is defined by NoneType')
                    else:
                        obj_collections_fields[obj_key][data_key] = obj_data_grid

                else:
                    obj_collections_fields[obj_key][data_key] = file_path_anc

            # Info ending
            log_stream.info(' ----> Get "' + obj_key + '" datasets ... DONE')

        return obj_collections_fields
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define merging info
    def define_merging_info(self, ws_collection_data, no_data=-9999):

        # Info start
        log_stream.info(' ----> Define merging info ... ')
        # Get merging method
        method_interpolate = self.method_interpolate_source

        log_stream.info(' -----> Select method "' + method_interpolate + '" ... ')
        if method_interpolate == 'sample':

            file_obj_terrain_ref = ws_collection_data['terrain_reference']
            file_obj_terrain_dom = ws_collection_data['terrain_dataset']

            if isinstance(file_obj_terrain_ref, dict) and file_obj_terrain_ref.__len__() == 1:
                file_name_terrain_ref = list(file_obj_terrain_ref.values())[0]
                obj_terrain_ref = read_obj(file_name_terrain_ref)

                geo_x_ref, geo_y_ref, geo_xllcorner_ref, \
                    geo_yllcorner_ref, geo_cellsize_ref = self.extract_geo_fields(obj_terrain_ref)

                grid_x_ref, grid_y_ref = np.meshgrid(geo_x_ref, geo_y_ref)

            else:
                log_stream.error(' ===> Terrain reference obj is not in supported format')
                raise NotImplementedError('Case not implemented yet')

            geo_idx_i_ref = np.zeros(shape=(grid_x_ref.shape[0], grid_y_ref.shape[1]))
            geo_idx_i_ref[:, :] = np.nan
            geo_idx_j_ref = np.zeros(shape=(grid_x_ref.shape[0], grid_y_ref.shape[1]))
            geo_idx_j_ref[:, :] = np.nan
            geo_mask_ref = np.zeros(shape=(grid_x_ref.shape[0], grid_y_ref.shape[1]))
            geo_mask_ref[:, :] = np.nan
            for id_dom, (key_dom, file_name_terrain_dom) in enumerate(file_obj_terrain_dom.items()):

                log_stream.info(' ------> Compute idxs between domain "' + key_dom + '" and domain reference ... ')

                obj_terrain_dom = read_obj(file_name_terrain_dom)
                geo_x_dom, geo_y_dom, geo_xllcorner_dom, \
                    geo_yllcorner_dom, geo_cellsize_dom = self.extract_geo_fields(obj_terrain_dom)

                if 'i_cols_ref' not in list(obj_terrain_dom.keys()) or 'j_rows_ref' not in list(obj_terrain_dom.keys()):

                    grid_x_dom, grid_y_dom = np.meshgrid(geo_x_dom, geo_y_dom)

                    geo_idx_i_dom = np.zeros(shape=(grid_x_dom.shape[0], grid_y_dom.shape[1]))
                    geo_idx_i_dom[:, :] = np.nan
                    geo_idx_j_dom = np.zeros(shape=(grid_x_dom.shape[0], grid_y_dom.shape[1]))
                    geo_idx_j_dom[:, :] = np.nan
                    for i in range(0, grid_x_dom.shape[0]):
                        for j in range(0, grid_y_dom.shape[1]):

                            i_cols = round((grid_x_dom[i, j] - geo_xllcorner_ref) / geo_cellsize_ref)
                            j_rows = round((grid_y_dom[i, j] - geo_yllcorner_ref) / geo_cellsize_ref)

                            j_rows = grid_y_ref.shape[0] - j_rows

                            if (0 <= j_rows < geo_mask_ref.shape[0]) and (0 <= i_cols < geo_mask_ref.shape[1]):

                                geo_idx_i_ref[i, j] = i_cols
                                geo_idx_j_ref[i, j] = j_rows
                                geo_idx_i_dom[i, j] = i
                                geo_idx_j_dom[i, j] = j

                                geo_mask_ref[j_rows, i_cols] = id_dom

                    # Check if the indexes are defined somewhere or not
                    geo_idx_all_undef = False
                    if np.isnan(geo_idx_i_ref).all():
                        geo_idx_all_undef = True
                        log_stream.warning(' ===> All indexes x of local domain in the reference domain are Nans'
                                           'The routine will exit with an error because all indexes are undefined')
                    if np.isnan(geo_idx_j_ref).all():
                        geo_idx_all_undef = True
                        log_stream.warning(' ===> All indexes y of local domain in the reference domain are Nans'
                                           'The routine will exit with an error because all indexes are undefined')

                    if geo_idx_all_undef:
                        log_stream.error(' ===> All indexes of local domain in the reference domain are undefined'
                                         'Check your grid in the configuration file')
                        raise RuntimeError('The indexes must be defined by a positive integer')

                    # Replace nan(s) with a no_data value (to convert the data to integer)
                    geo_idx_i_ref[np.isnan(geo_idx_i_ref)] = no_data
                    geo_idx_j_ref[np.isnan(geo_idx_j_ref)] = no_data

                    obj_terrain_dom['i_cols_ref'] = geo_idx_i_ref.astype(int)
                    obj_terrain_dom['j_rows_ref'] = geo_idx_j_ref.astype(int)
                    obj_terrain_dom['i_cols_dom'] = geo_idx_i_dom.astype(int)
                    obj_terrain_dom['j_rows_dom'] = geo_idx_j_dom.astype(int)

                    if os.path.exists(file_name_terrain_dom):
                        os.remove(file_name_terrain_dom)

                    write_obj(file_name_terrain_dom, obj_terrain_dom)

                    log_stream.info(' ------> Compute idxs between domain "' + key_dom +
                                    '" and domain reference ... DONE')

                else:
                    log_stream.info(' ------> Compute idxs between domain "' + key_dom +
                                    '" and domain reference ... SKIPPED. Datasets are previously computed.')

        elif method_interpolate == 'nearest':
            log_stream.info(' -----> Select method "' + method_interpolate + '" ... DONE')
        else:
            log_stream.info(' -----> Select method "' + method_interpolate + '" ... FAILED')
            log_stream.error(' ===> Merging method not available')
            raise NotImplementedError('Case not implemented yet')

        # Info end
        log_stream.info(' ----> Define merging info ... DONE')
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize geographical data
    def organize_static(self):

        # Info start
        log_stream.info(' ---> Organize static datasets ... ')

        # Get static objects
        obj_src = self.src_obj
        obj_anc = self.anc_obj
        obj_dst = self.dst_obj

        # Get data collections obj
        collections_src = self.get_collections_fields(obj_src, obj_anc)
        collections_dst = self.get_collections_fields(obj_dst, obj_anc)

        # Add merging method info
        self.define_merging_info(collections_src)

        # Store workspace collections obj
        ws_collections_data = {self.flag_dset_source: collections_src, self.flag_dset_destination: collections_dst}

        # Info end
        log_stream.info(' ---> Organize static datasets ... DONE')

        return ws_collections_data
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
