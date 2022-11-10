"""
Class Features

Name:          drv_dataset_hmc_base_source
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging

import pandas as pd

from copy import deepcopy

from hmc.algorithm.utils.lib_utils_dict import set_dict_values, lookup_dict_keys
from hmc.algorithm.utils.lib_utils_geo import compute_section_mask
from hmc.algorithm.default.lib_default_args import logger_name

from hmc.driver.dataset.drv_dataset_hmc_io_static import DSetManager as DSetManager_Static
from hmc.driver.dataset.drv_dataset_hmc_io_dynamic_restart import DSetManager as DSetManager_Restart
from hmc.driver.dataset.drv_dataset_hmc_io_dynamic_forcing import DSetManager as DSetManager_DynamicForcing
from hmc.driver.dataset.drv_dataset_hmc_io_dynamic_updating import DSetManager as DSetManager_DynamicUpdating

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Class to read model datasets
class ModelSource:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self, datasets_obj,
                 tag_dset_geo='DataGeo',
                 tag_dset_forcing='DataForcing', tag_dset_updating='DataUpdating',
                 tag_dset_restart='DataRestart', tag_dset_observed='DataObs',
                 template_time=None,
                 template_run_ref=None,
                 template_run_path=None,
                 template_run_def=None,
                 template_analysis_def=None,
                 template_static=None, template_dynamic=None, **kwargs):

        self.dset_obj = datasets_obj

        self.dset_geo = self.dset_obj[tag_dset_geo]
        self.dset_restart = self.dset_obj[tag_dset_restart]
        # self.dset_observed = self.dset_obj[tag_dset_observed]

        dset_forcing = self.dset_obj[tag_dset_forcing]
        dset_updating = self.dset_obj[tag_dset_updating]

        #dset_forcing = merge_structure(
        #    dset_forcing, dset_updating, keys_target_list=['Gridded', 'hmc_file_variable', 'OBS', 'var_list'])
        #dset_forcing = merge_structure(
        #    dset_forcing, dset_updating, keys_target_list=['Gridded', 'hmc_file_variable', 'OBS', 'var_operation'])

        self.dset_forcing = dset_forcing
        self.dset_updating = dset_updating

        self.obj_template_time = template_time
        self.obj_template_run_def = template_run_def
        self.obj_template_run_ref = template_run_ref
        self.obj_template_run_path = template_run_path
        self.obj_template_analysis_def = template_analysis_def
        self.obj_template_dset_static_ref = template_static
        self.obj_template_dset_dynamic_ref = template_dynamic

        self.tag_model = 'hmc'
        self.tag_datasets = 'datasets'

        self.tag_dam_list = 'dam_name_list'
        self.tag_lake_list = 'lake_name_list'
        self.tag_plant_list = 'plant_name_list'
        self.tag_release_list = 'release_name_list'
        self.tag_basin_list = 'basin_name_list'
        self.tag_section_list = 'section_name_list'
        self.tag_outlet_list = 'outlet_name_list'
        self.tag_dam_system_list = 'dam_system_name_list'
        self.tag_mask_list = 'mask_name_list'

        self.list_sep = ':'
        self.sublist_sep = '_'

        self.reader_geo = DSetManager_Static(dset=self.dset_geo,
                                             template_static_ref=self.obj_template_dset_static_ref,
                                             template_run_ref=self.obj_template_run_ref,
                                             template_run_def=self.obj_template_run_def)

        self.reader_restart = DSetManager_Restart(
            dset=self.dset_restart,
            terrain_values=self.reader_geo.dset_static_ref['values'],
            terrain_geo_x=self.reader_geo.dset_static_ref['longitude'],
            terrain_geo_y=self.reader_geo.dset_static_ref['latitude'],
            terrain_transform=self.reader_geo.dset_static_ref['transform'],
            terrain_bbox=self.reader_geo.dset_static_ref['bbox'],
            dset_list_type=['ARCHIVE'],
            model_tag=self.tag_model, datasets_tag=self.tag_datasets,
            template_time=self.obj_template_time, template_analysis_def=self.obj_template_analysis_def)

        self.vars_restart_analysis = {
            'Gridded': ['DFE', 'HydroLevelC', 'HydroLevelH', 'Qup', 'LST', 'VTot', 'VRet', 'Routing', 'WTLevel'],
            'Point': 'ALL'
        }

        self.reader_forcing = DSetManager_DynamicForcing(
            dset=self.dset_forcing,
            terrain_values=self.reader_geo.dset_static_ref['values'],
            terrain_geo_x=self.reader_geo.dset_static_ref['longitude'],
            terrain_geo_y=self.reader_geo.dset_static_ref['latitude'],
            terrain_transform=self.reader_geo.dset_static_ref['transform'],
            terrain_bbox=self.reader_geo.dset_static_ref['bbox'],
            dset_list_type=['OBS', 'FOR'],
            model_tag=self.tag_model, datasets_tag=self.tag_datasets,
            template_time=self.obj_template_time, template_analysis_def=self.obj_template_analysis_def,
            file_compression_mode=True)

        self.vars_forcing_analysis = {
            'Gridded': 'ALL', 'Point': 'ALL', 'TimeSeries': 'ALL'
        }

        self.reader_updating = DSetManager_DynamicUpdating(
            dset=self.dset_updating,
            terrain_values=self.reader_geo.dset_static_ref['values'],
            terrain_geo_x=self.reader_geo.dset_static_ref['longitude'],
            terrain_geo_y=self.reader_geo.dset_static_ref['latitude'],
            terrain_transform=self.reader_geo.dset_static_ref['transform'],
            terrain_bbox=self.reader_geo.dset_static_ref['bbox'],
            dset_list_type=['OBS'],
            model_tag=self.tag_model, datasets_tag=self.tag_datasets,
            template_time=self.obj_template_time, template_analysis_def=self.obj_template_analysis_def,
            file_compression_mode=True)

        self.vars_updating_analysis = {}

        '''
        self.reader_observed = DSetManager_Dynamic(
            dset=self.dset_observed,
            terrain_values=self.reader_geo.dset_static_ref['values'],
            terrain_geo_x=self.reader_geo.dset_static_ref['longitude'],
            terrain_geo_y=self.reader_geo.dset_static_ref['latitude'],
            terrain_transform=self.reader_geo.dset_static_ref['transform'],
            terrain_bbox=self.reader_geo.dset_static_ref['bbox'],
            dset_list_type=['ARCHIVE'],
            model_tag=self.tag_model, datasets_tag=self.tag_datasets, template_time=self.obj_template_time)
        '''
        self.dset_collections_static = None
        self.dset_collections_dynamic = None

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to analyze static datasets and model
    def analyze_data_static(self, obj_static_datasets, tag_datatype='LAND', tag_datadriver='static'):

        # Start info
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... ')

        reader_dataset = self.reader_geo
        dset_collections_static = self.dset_collections_static

        dset_source_frame_merge = None
        for file_type, dset_source_subset_static in obj_static_datasets.items():

            var_data_dict = {}
            for var_check in list(dset_source_subset_static['file_check'].keys()):
                var_data_dict[var_check] = None
                if dset_collections_static is not None:
                    if var_check in list(dset_collections_static.keys()):
                        var_data_dict[var_check] = dset_collections_static[var_check]

            dset_source_subset_static = obj_static_datasets[file_type]
            dset_source_frame_raw = reader_dataset.collect_data(dset_source_subset_static,
                                                                data_source_static=var_data_dict)

            if dset_source_frame_merge is None:
                dset_source_frame_merge = deepcopy(dset_source_frame_raw)
                dset_collections_static = dset_source_frame_merge[reader_dataset.datasets_tag]
            else:
                dset_source_values_merged = dset_source_frame_merge[reader_dataset.datasets_tag]
                dset_source_values_raw = dset_source_frame_raw[reader_dataset.datasets_tag]

                var_list_merged = list(dset_source_values_merged.keys())
                var_list_raw = list(dset_source_values_raw.keys())
                var_list_tmp = list(set(var_list_merged + var_list_raw))

                dset_source_values_tmp = {}
                for var_key in var_list_tmp:

                    if var_key in list(dset_source_values_merged.keys()):
                        var_fields_merged = dset_source_values_merged[var_key]
                    else:
                        var_fields_merged = None
                    if var_key in list(dset_source_values_raw.keys()):
                        var_fields_raw = dset_source_values_raw[var_key]
                    else:
                        var_fields_raw = None

                    if (var_fields_merged is not None) and (var_fields_raw is not None):
                        var_fields_tmp = {**var_fields_merged, **var_fields_raw}
                    elif (var_fields_merged is not None) and (var_fields_raw is None):
                        var_fields_tmp = deepcopy(var_fields_merged)
                    elif (var_fields_merged is None) and (var_fields_raw is not None):
                        var_fields_tmp = deepcopy(var_fields_raw)
                    elif (var_fields_merged is None) and (var_fields_raw is None):
                        var_fields_tmp = None
                    else:
                        log_stream.error(' ===> Type of format for variable "' + var_key + '" is not supported')
                        raise IOError('Unexpected type of object, check the procedure.')

                    dset_source_values_tmp[var_key] = var_fields_tmp

                dset_source_frame_merge[reader_dataset.datasets_tag] = dset_source_values_tmp

                dset_collections_static = dset_source_frame_merge[reader_dataset.datasets_tag]

        # Get static point information for dam(s) and section(s)
        if 'Dam' in list(dset_collections_static.keys()):

            if dset_collections_static['Dam'] is not None:
                dam_list = list(dset_collections_static['Dam'].keys())
                dam_parts = split_dict_keys(dam_list)
                if dam_parts.__len__() == 2:
                    dam_list = dam_parts[0]
                    plant_list = dam_parts[1]
                elif dam_parts.__len__() == 1:
                    dam_list = dam_parts[0]
                    plant_list = dam_parts[0]
                else:
                    log_stream.error(' ===> Dam parts are in a unsupported format')
                    raise NotImplementedError('Case not implemented yet')

                if dam_list.__len__() != plant_list.__len__():
                    log_stream.error(' ===> Dams list and plants list have not the same elements length')
                    raise NotImplementedError('Case not implemented yet')

                dam_system_dict = {}
                for dam_step, plant_step in zip(dam_list, plant_list):
                    if dam_step not in list(dam_system_dict.keys()):
                        dam_system_dict[dam_step] = [plant_step]
                    else:
                        tmp_step = dam_system_dict[dam_step]
                        tmp_step.append(plant_step)
                        dam_system_dict[dam_step] = tmp_step

                dam_system_list = []
                for dam_system_name_str, dam_system_plant_list in dam_system_dict.items():
                    dam_system_name_value = self.sublist_sep.join(dam_system_plant_list)
                    dam_system_conn_str = self.list_sep.join([dam_system_name_str, dam_system_name_value])
                    dam_system_list.append(dam_system_conn_str)

            else:
                dam_system_list = None
                dam_list = None
                plant_list = None
        else:
            log_stream.error(' ===> "Dam" key in static collections does not exist')
            raise NotImplementedError('Key not available in data collections')

        if 'Lake' in list(dset_collections_static.keys()):                                # add20221108 --start

            if dset_collections_static['Lake'] is not None:
                lake_list = list(dset_collections_static['Lake'].keys())
            else:
                lake_list = None
        else:
            log_stream.error(' ===> "Lake" key in static collections does not exist')
            raise NotImplementedError('Key not available in data collections')              # add20221108 --end

        if 'Intake' in list(dset_collections_static.keys()):                                # add20210604 --start

            if dset_collections_static['Intake'] is not None:
                intake_list = list(dset_collections_static['Intake'].keys())
                lakes_parts = split_dict_keys(intake_list)
                if lakes_parts.__len__() == 2:
                    release_list = lakes_parts[0]
                    socket_list = lakes_parts[1]
                else:
                    log_stream.error(' ===> Intake parts are in a unsupported format')
                    raise NotImplementedError('Case not implemented yet')
            else:
                release_list = None
                socket_list = None
        else:
            log_stream.error(' ===> "Intake" key in static collections does not exist')
            raise NotImplementedError('Key not available in data collections')              # add20210604 --end

        if 'Section' in list(dset_collections_static.keys()):
            section_list = list(dset_collections_static['Section'].keys())
            section_parts = split_dict_keys(section_list)

            outlet_list = []
            for basin, section in zip(section_parts[0], section_parts[1]):
                outlet_step = self.list_sep.join([basin, section])
                outlet_list.append(outlet_step)

        else:
            log_stream.error(' ===> "Section" key in static collections does not exist')
            raise NotImplementedError('Key not available in data collections')

        if ('Section' in list(dset_collections_static.keys())) and (
                'Flow_Directions' in list(dset_collections_static.keys())):

            geo_fdir_values = dset_collections_static['Flow_Directions'].values
            section_reference = dset_collections_static['Section']
            geo_reference = self.reader_geo.dset_static_ref

            mask_obj = compute_section_mask(geo_fdir_values, geo_reference=geo_reference, section_reference=section_reference)

        else:
            mask_obj = None
            log_stream.warning(' ===> "Section" or/and "Flow_Directions" keys in static collections does not exist')

        if release_list is not None:                                            #add20210607 ---start
            if plant_list is None:
                plant_list = deepcopy(release_list)
            else:
                plant_list = dam_system_list + release_list
        #else:
        #    plant_list = dam_system_list #add20210607 ---end

        dset_collections_static[self.tag_dam_list] = dam_list
        dset_collections_static[self.tag_plant_list] = plant_list
        dset_collections_static[self.tag_lake_list] = lake_list
        dset_collections_static[self.tag_dam_system_list] = dam_system_list
        dset_collections_static[self.tag_release_list] = release_list
        dset_collections_static[self.tag_basin_list] = section_parts[0]
        dset_collections_static[self.tag_section_list] = section_parts[1]
        dset_collections_static[self.tag_outlet_list] = outlet_list
        dset_collections_static[self.tag_mask_list] = mask_obj

        # Dump data in class environment
        self.dset_collections_static = dset_collections_static

        # Ending info
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... DONE')

        return dset_collections_static

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to analyze restart datasets and model
    def analyze_data_dynamic_restart(self, obj_time_series, obj_time_info,
                                     obj_static_datasets, obj_dynamic_datasets,
                                     obj_run_settings, obj_run_path,
                                     tag_datatype='OBS', tag_datadriver='restart',
                                     idx_ts_subselect=0):

        # Starting info
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... ')

        if tag_datadriver == 'restart':
            reader_dataset = self.reader_restart
        else:
            log_stream.error(' ===> Source datasets driver is not allowed')
            raise RuntimeError('Bad definition of datasets driver')
        dset_collections_dynamic_in = self.dset_collections_dynamic

        obj_dset_base = swap_dict_keys(reader_dataset.dset_obj)
        fx_dset_base = swap_dict_keys(reader_dataset.dset_fx)

        vars_dataset = reader_dataset.dset_vars

        dset_collections_dynamic_out = {}
        for (run_key, obj_ts_step), obj_ti_step, obj_dset_step in zip(obj_time_series.items(), obj_time_info.values(),
                                                                      obj_dynamic_datasets.values()):
            # info
            log_stream.info(' -----> Run ' + run_key + ' ... ')

            if (dset_collections_dynamic_in is not None) and (run_key in list(dset_collections_dynamic_in.keys())):
                dset_collections_dynamic_tmp = deepcopy(dset_collections_dynamic_in[run_key])
            else:
                dset_collections_dynamic_tmp = None

            dset_path_tmp = obj_run_path[run_key]['tmp']
            dset_clean_tmp = obj_run_settings[run_key]['run_clean_tmp']

            dset_time = obj_ts_step.index[idx_ts_subselect]

            dset_model_dyn = obj_dset_step[self.tag_model]
            dset_source_dyn = obj_dset_step[self.tag_datasets]

            dset_model_base = obj_dset_base[self.tag_model]
            dset_source_base = obj_dset_base[self.tag_datasets]

            fx_source_base = fx_dset_base[self.tag_datasets]

            if dset_collections_dynamic_tmp is None:
                index_ts_expected = obj_ts_step.index
                values_ts_expected = {'File_Type': obj_ts_step['File_Type'].values}
                dset_collections_dynamic_tmp = pd.DataFrame(values_ts_expected, index=index_ts_expected)
                dset_collections_dynamic_tmp.index.name = 'time'

            start_idx_subselect = dset_time
            end_idx_subselect = dset_time

            for file_type in list(dset_source_dyn.keys()):

                # Info
                log_stream.info(' ------> Datasets ' + file_type + ' ... ')

                # Selection based on type and indexes
                dset_model_type_dyn = dset_model_dyn[file_type]
                dset_source_type_dyn = dset_source_dyn[file_type]

                dset_source_subset_base = dset_source_base[file_type][tag_datatype]
                fx_source_subset_base = fx_source_base[file_type][tag_datatype]

                # Collect data
                dset_source_frame_raw = reader_dataset.collect_data(
                    dset_model_type_dyn, dset_source_type_dyn, dset_source_subset_base,
                    dset_static_info=obj_static_datasets,
                    dset_time_info=obj_ti_step,
                    dset_time_start=start_idx_subselect, dset_time_end=end_idx_subselect,
                    path_tmp=dset_path_tmp, clean_tmp=dset_clean_tmp,
                    plant_name_list=obj_static_datasets[self.tag_plant_list], 
                    release_name_list=obj_static_datasets[self.tag_release_list], 
                    lake_name_list=obj_static_datasets[self.tag_lake_list])			#add20210608_last_arg

                # Check collected data
                if dset_source_frame_raw[self.tag_datasets] is not None:

                    # Get analysis vars
                    if self.vars_restart_analysis is not None:
                        if file_type in list(self.vars_restart_analysis.keys()):
                            vars_analysis = self.vars_restart_analysis[file_type]
                        else:
                            vars_analysis = None
                    else:
                        vars_analysis = None

                    # Organize data
                    dset_source_frame_values_def, dset_source_frame_ts_def = reader_dataset.organize_data(
                        dset_time, dset_source_frame_raw, dset_variable_selected=vars_analysis)
                    # Freeze data
                    dset_collections_dynamic_tmp = reader_dataset.freeze_data(
                        deepcopy(dset_collections_dynamic_tmp), dset_source_frame_ts_def)

                    # Dump or copy data
                    if fx_source_subset_base['dump']:
                        reader_dataset.dump_data(dset_model_type_dyn, idx_ts_subselect, dset_source_frame_values_def)
                    elif fx_source_subset_base['copy']:
                        reader_dataset.copy_data(dset_model_type_dyn, dset_source_type_dyn,
                                                 vars_selected=vars_dataset)
                    # Info
                    log_stream.info(' ------> Datasets ' + file_type + ' ... DONE')
                else:
                    # Info
                    log_stream.info(' ------> Datasets ' + file_type + ' ... SKIPPED. Datasets are undefined')

            dset_collections_dynamic_out[run_key] = dset_collections_dynamic_tmp
            # Dump data in class environment
            if self.dset_collections_dynamic is None:
                self.dset_collections_dynamic = {}
            self.dset_collections_dynamic[run_key] = dset_collections_dynamic_tmp

            # Ending info
            log_stream.info(' -----> Run ' + run_key + ' ... DONE')

        # Ending info for routine
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... DONE')

        return dset_collections_dynamic_out

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to analyze dynamic forcing datasets and model
    def analyze_data_dynamic_forcing(self, obj_time_series, obj_time_info,
                                     obj_static_datasets, obj_dynamic_datasets,
                                     obj_run_settings, obj_run_path,
                                     tag_datatype='OBS', tag_datadriver='forcing'):

        # Starting info for routine
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... ')

        if tag_datadriver == 'forcing':
            reader_dataset = self.reader_forcing
        else:
            log_stream.error(' ===> Source datasets driver is not allowed')
            raise RuntimeError('Bad definition of datasets driver')
        dset_collections_dynamic_in = self.dset_collections_dynamic

        obj_dset_base = swap_dict_keys(reader_dataset.dset_obj)
        fx_dset_base = swap_dict_keys(reader_dataset.dset_fx)

        vars_dataset = reader_dataset.dset_vars

        dset_collections_dynamic_out = {}
        for (run_key, obj_ts_step), obj_ti_step, obj_dset_step in zip(obj_time_series.items(), obj_time_info.values(),
                                                                      obj_dynamic_datasets.values()):
            # info
            log_stream.info(' -----> Run ' + run_key + ' ... ')

            if (dset_collections_dynamic_in is not None) and (run_key in list(dset_collections_dynamic_in.keys())):
                dset_collections_dynamic_tmp = deepcopy(dset_collections_dynamic_in[run_key])
            else:
                dset_collections_dynamic_tmp = None

            dset_path_tmp = obj_run_path[run_key]['tmp']
            dset_clean_tmp = obj_run_settings[run_key]['run_clean_tmp']

            obj_ts_select = obj_ts_step.loc[obj_ts_step['File_Type'] == tag_datatype]
            id_ts_select = list(set(obj_ts_select['File_Group'].values))

            dset_model_dyn = obj_dset_step[self.tag_model]
            dset_source_dyn = obj_dset_step[self.tag_datasets]

            dset_model_base = obj_dset_base[self.tag_model]
            dset_source_base = obj_dset_base[self.tag_datasets]
            fx_source_base = fx_dset_base[self.tag_datasets]

            if dset_collections_dynamic_tmp is None:
                index_ts_expected = obj_ts_step.index
                values_ts_expected = {'File_Type': obj_ts_step['File_Type'].values}
                dset_collections_dynamic_tmp = pd.DataFrame(values_ts_expected, index=index_ts_expected)
                dset_collections_dynamic_tmp.index.name = 'time'

            for id_ts_step in id_ts_select:

                obj_ts_subselect = obj_ts_select.loc[obj_ts_select['File_Group'] == int(id_ts_step)]
                idx_ts_subselect = obj_ts_subselect.index

                start_idx_subselect = idx_ts_subselect[0]
                end_idx_subselect = idx_ts_subselect[-1]

                for file_type in list(dset_source_dyn.keys()):

                    # Info
                    log_stream.info(' ------> Datasets ' + file_type + ' ... ')

                    # Selection based on type and indexes
                    dset_model_type_dyn = dset_model_dyn[file_type]
                    dset_source_type_dyn = dset_source_dyn[file_type]

                    dset_source_subset_base = dset_source_base[file_type][tag_datatype]
                    fx_source_subset_base = fx_source_base[file_type][tag_datatype]

                    dset_model_subset_dyn = dset_model_type_dyn[start_idx_subselect:end_idx_subselect]
                    dset_source_subset_dyn = dset_source_type_dyn[start_idx_subselect:end_idx_subselect]

                    # Validate selected flag
                    reader_dataset.validate_flag(tag_datadriver, fx_source_subset_base)

                    # Collect data
                    dset_source_frame_raw_base = reader_dataset.collect_data(
                        dset_model_subset_dyn, dset_source_subset_dyn, dset_source_subset_base,
                        dset_static_info=obj_static_datasets,
                        dset_time_info=obj_ti_step,
                        dset_time_start=start_idx_subselect, dset_time_end=end_idx_subselect,
                        path_tmp=dset_path_tmp, clean_tmp=dset_clean_tmp,
                        plant_name_list=obj_static_datasets[self.tag_plant_list],
                        release_name_list=obj_static_datasets[self.tag_release_list])			#add20210608_last_arg

                    # Check collected data
                    if dset_source_frame_raw_base[self.tag_datasets] is not None:

                        # Get analysis vars
                        if self.vars_forcing_analysis is not None:
                            if file_type in list(self.vars_forcing_analysis.keys()):
                                vars_analysis = self.vars_forcing_analysis[file_type]
                            else:
                                vars_analysis = None
                        else:
                            vars_analysis = None

                        # Organize data
                        dset_source_frame_values_def,  dset_source_frame_ts_def = reader_dataset.organize_data(
                            idx_ts_subselect, dset_source_frame_raw_base,
                            dset_static=obj_static_datasets, dset_variable_selected=vars_analysis)
                        # Freeze data
                        dset_collections_dynamic_tmp = reader_dataset.freeze_data(
                            deepcopy(dset_collections_dynamic_tmp), dset_source_frame_ts_def)

                        # Dump or copy data
                        if fx_source_subset_base['dump']:
                            reader_dataset.dump_data(dset_model_subset_dyn, idx_ts_subselect, dset_source_frame_values_def)
                        elif fx_source_subset_base['copy']:
                            reader_dataset.copy_data(dset_model_subset_dyn, dset_source_subset_dyn,
                                                     vars_selected=vars_dataset)
                        else:
                            log_stream.error(' ===> Source datasets operation not permitted')
                            raise NotImplementedError('Case not implemented yet')

                        # Info
                        log_stream.info(' ------> Datasets ' + file_type + ' ... DONE')
                    else:
                        # Info
                        log_stream.info(' ------> Datasets ' + file_type + ' ... SKIPPED. Datasets are undefined')

            # Dump data in dictionary
            dset_collections_dynamic_out[run_key] = dset_collections_dynamic_tmp
            # Dump data in class environment
            if self.dset_collections_dynamic is None:
                self.dset_collections_dynamic = {}
            self.dset_collections_dynamic[run_key] = dset_collections_dynamic_tmp

            # Ending info
            log_stream.info(' -----> Run ' + run_key + ' ... DONE')

        # Ending info for routine
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... DONE')

        return dset_collections_dynamic_out
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to analyze dynamic updating datasets and model
    def analyze_data_dynamic_updating(self, obj_time_series, obj_time_info,
                                      obj_static_datasets, obj_dynamic_datasets,
                                      obj_run_settings, obj_run_path,
                                      tag_datatype='OBS', tag_datadriver='updating'):

        # Starting info for routine
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... ')

        if tag_datadriver == 'updating':
            reader_dataset = self.reader_updating
        else:
            log_stream.error(' ===> Source datasets driver is not allowed')
            raise RuntimeError('Bad definition of datasets driver')
        dset_collections_dynamic_in = self.dset_collections_dynamic

        obj_dset_base = swap_dict_keys(reader_dataset.dset_obj)
        fx_dset_base = swap_dict_keys(reader_dataset.dset_fx)

        vars_dataset = reader_dataset.dset_vars

        dset_collections_dynamic_out = {}
        for (run_key, obj_ts_step), obj_ti_step, obj_dset_step in zip(obj_time_series.items(), obj_time_info.values(),
                                                                      obj_dynamic_datasets.values()):
            # info
            log_stream.info(' -----> Run ' + run_key + ' ... ')

            if (dset_collections_dynamic_in is not None) and (run_key in list(dset_collections_dynamic_in.keys())):
                dset_collections_dynamic_tmp = deepcopy(dset_collections_dynamic_in[run_key])
            else:
                dset_collections_dynamic_tmp = None

            dset_path_tmp = obj_run_path[run_key]['tmp']
            dset_clean_tmp = obj_run_settings[run_key]['run_clean_tmp']

            obj_ts_select = obj_ts_step.loc[obj_ts_step['File_Type'] == tag_datatype]
            id_ts_select = list(set(obj_ts_select['File_Group'].values))

            dset_model_dyn = obj_dset_step[self.tag_model]
            dset_source_dyn = obj_dset_step[self.tag_datasets]

            dset_model_base = obj_dset_base[self.tag_model]
            dset_source_base = obj_dset_base[self.tag_datasets]
            fx_source_base = fx_dset_base[self.tag_datasets]

            if dset_collections_dynamic_tmp is None:
                index_ts_expected = obj_ts_step.index
                values_ts_expected = {'File_Type': obj_ts_step['File_Type'].values}
                dset_collections_dynamic_tmp = pd.DataFrame(values_ts_expected, index=index_ts_expected)
                dset_collections_dynamic_tmp.index.name = 'time'

            for id_ts_step in id_ts_select:

                obj_ts_subselect = obj_ts_select.loc[obj_ts_select['File_Group'] == int(id_ts_step)]
                idx_ts_subselect = obj_ts_subselect.index

                start_idx_subselect = idx_ts_subselect[0]
                end_idx_subselect = idx_ts_subselect[-1]

                for file_type in list(dset_source_dyn.keys()):

                    # Info
                    log_stream.info(' ------> Datasets ' + file_type + ' ... ')

                    # Selection based on type and indexes
                    dset_model_type_dyn = dset_model_dyn[file_type]
                    dset_source_type_dyn = dset_source_dyn[file_type]

                    dset_source_subset_base = dset_source_base[file_type][tag_datatype]
                    fx_source_subset_base = fx_source_base[file_type][tag_datatype]

                    dset_model_subset_dyn = dset_model_type_dyn[start_idx_subselect:end_idx_subselect]
                    dset_source_subset_dyn = dset_source_type_dyn[start_idx_subselect:end_idx_subselect]

                    # Validate selected flag
                    reader_dataset.validate_flag(tag_datadriver, fx_source_subset_base)

                    # Collect data
                    dset_source_frame_raw_base = reader_dataset.collect_data(
                        dset_model_subset_dyn, dset_source_subset_dyn, dset_source_subset_base,
                        dset_static_info=obj_static_datasets,
                        dset_time_info=obj_ti_step,
                        dset_time_start=start_idx_subselect, dset_time_end=end_idx_subselect,
                        path_tmp=dset_path_tmp, clean_tmp=dset_clean_tmp,
                        plant_name_list=obj_static_datasets[self.tag_plant_list],
                        release_name_list=obj_static_datasets[self.tag_release_list])				#add20210608_last_arg

                    # Check collected data
                    if dset_source_frame_raw_base[self.tag_datasets] is not None:

                        # Get analysis vars
                        if self.vars_forcing_analysis is not None:
                            if file_type in list(self.vars_forcing_analysis.keys()):
                                vars_analysis = self.vars_forcing_analysis[file_type]
                            else:
                                vars_analysis = None
                        else:
                            vars_analysis = None

                        # Organize data
                        dset_source_frame_values_def, dset_source_frame_ts_def = reader_dataset.organize_data(
                            idx_ts_subselect, dset_source_frame_raw_base, dset_variable_selected=vars_analysis)
                        # Freeze data
                        dset_collections_dynamic_tmp = reader_dataset.freeze_data(
                            deepcopy(dset_collections_dynamic_tmp), dset_source_frame_ts_def)

                        # Dump or copy data
                        if fx_source_subset_base['dump']:
                            reader_dataset.dump_data(dset_model_subset_dyn, idx_ts_subselect, dset_source_frame_values_def)
                        elif fx_source_subset_base['copy']:
                            reader_dataset.copy_data(dset_model_subset_dyn, dset_source_subset_dyn,
                                                     vars_selected=vars_dataset)
                        else:
                            log_stream.error(' ===> Source datasets operation not permitted')
                            raise NotImplementedError('Case not implemented yet')

                        # Info
                        log_stream.info(' ------> Datasets ' + file_type + ' ... DONE')
                    else:
                        # Info
                        log_stream.info(' ------> Datasets ' + file_type + ' ... SKIPPED. Datasets are undefined')

            # Dump data in dictionary
            dset_collections_dynamic_out[run_key] = dset_collections_dynamic_tmp
            # Dump data in class environment
            if self.dset_collections_dynamic is None:
                self.dset_collections_dynamic = {}
            self.dset_collections_dynamic[run_key] = dset_collections_dynamic_tmp

            # Ending info
            log_stream.info(' -----> Run ' + run_key + ' ... DONE')

        # Ending info for routine
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... DONE')

        return dset_collections_dynamic_out
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize dynamic datasets and model
    def organize_data_dynamic(self, time_series_collections, template_run_filled, template_run_path,
                              static_datasets_collections=None, tag_datadriver='forcing'):

        # Starting information
        log_stream.info(' ----> Organize dynamic datasets ... ')

        if tag_datadriver == 'restart':
            reader_dataset = self.reader_restart
        elif tag_datadriver == 'forcing':
            reader_dataset = self.reader_forcing
        elif tag_datadriver == 'updating':
            reader_dataset = self.reader_updating
        else:
            log_stream.error(' ===> Source datasets driver is not allowed')
            raise RuntimeError('Bad definition of datasets driver')

        if static_datasets_collections is not None:
            extra_args = {'dset_var_name_forcing_ts_plant': static_datasets_collections[self.tag_plant_list]}
        else:
            extra_args = None

        template_run_ref = self.obj_template_run_ref
        template_dynamic_ref = self.obj_template_dset_dynamic_ref

        template_run_merge = {**template_run_ref, **template_dynamic_ref}

        obj_dynamic_datasets = {}
        for (run_key, time_series_step), (template_run_settings_step), (template_run_path_step) in zip(
                time_series_collections.items(), template_run_filled.values(), template_run_path.values()):

            log_stream.info(' -----> Run ' + run_key + ' ... ')

            obj_datasets, obj_model = reader_dataset.collect_filename(
                time_series_step, template_run_merge, template_run_settings_step, template_run_path_step,
                extra_dict=extra_args)

            obj_dynamic_datasets[run_key] = {}
            obj_dynamic_datasets[run_key][self.tag_model] = obj_model
            obj_dynamic_datasets[run_key][self.tag_datasets] = obj_datasets

            log_stream.info(' -----> Run ' + run_key + ' ... DONE')

        # Starting information
        log_stream.info(' ----> Organize dynamic datasets ... DONE')

        return obj_dynamic_datasets
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize restart datasets and model
    def organize_data_restart(self, time_series_collections, template_run_filled):

        # Starting information
        log_stream.info(' ----> Organize restart datasets ... ')

        template_run_ref = self.obj_template_run_ref
        template_run_path = self.obj_template_run_path
        template_dynamic_ref = self.obj_template_dset_dynamic_ref

        template_run_merge = {**template_run_ref, **template_dynamic_ref}

        template_dynamic_filled = {}

        obj_restart_datasets = {}
        for (run_key, time_series_step), (template_run_step) in zip(
                time_series_collections.items(), template_run_filled.values()):

            log_stream.info(' -----> Run ' + run_key + ' ... ')

            template_dynamic_step = {**template_run_step, **template_dynamic_filled}

            obj_datasets, obj_model = self.reader_restart.collect_filename(
                time_series_step, template_run_merge, template_dynamic_step)

            obj_restart_datasets[run_key] = {}
            obj_restart_datasets[run_key][self.tag_model] = obj_model
            obj_restart_datasets[run_key][self.tag_datasets] = obj_datasets

            log_stream.info(' -----> Run ' + run_key + ' ... ')

        # Ending information
        log_stream.info(' ----> Organize restart datasets ... DONE')

        return obj_restart_datasets

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize dynamic datasets and model
    def organize_data_static(self, template_filled):

        # Starting information
        log_stream.info(' ----> Organize static datasets ... ')

        template_run_ref = self.obj_template_run_ref
        template_static_ref = self.obj_template_dset_static_ref

        template_ref = {**template_run_ref, **template_static_ref}

        obj_static_datasets = self.reader_geo.collect_filename(template_ref, template_filled)

        # Ending information
        log_stream.info(' ----> Organize static datasets ... DONE')

        return obj_static_datasets

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to merge driver structure
def merge_structure(dset_ref, dset_ancillary, keys_target_list=None):

    if keys_target_list is None:
        keys_target_list = ['Gridded', 'hmc_file_variable', 'OBS', 'var_list']

    dset_ref_items = lookup_dict_keys(dset_ref, keys_target_list)
    dset_ancillary_items = lookup_dict_keys(dset_ancillary, keys_target_list)

    if isinstance(dset_ref_items, dict) and isinstance(dset_ancillary_items, dict):
        dset_merge_items = {**dset_ref_items, **dset_ancillary_items}
        dset_tmp_items = deepcopy(dset_ref)
        dset_filled_items = set_dict_values(dset_tmp_items, keys_target_list, dset_merge_items)
    else:
        logging.error(' ===> Object type of ref or/and ancillary are not allowed')
        raise NotImplementedError('Objects are not implemented')

    return dset_filled_items
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to split dictionary keys
def split_dict_keys(key_list, key_delimiter=':'):
    key_parts = None
    for key_step in key_list:
        key_split = key_step.split(key_delimiter)
        if key_parts is None:
            key_parts = [[] for i in range(key_split.__len__())]
        for key_id, key_split_step in enumerate(key_split):
            key_parts[key_id].append(key_split_step)
    return key_parts
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to swap dictionary two order keys
def swap_dict_keys(dict_order_x_y):
    dict_order_y_x = {}
    for dset_key, dset_ws in dict_order_x_y.items():
        for dset_type, dset_vars in dset_ws.items():
            if dset_type not in list(dict_order_y_x.keys()):
                dict_order_y_x[dset_type] = {}
            if dset_key not in list(dict_order_y_x[dset_type].keys()):
                dict_order_y_x[dset_type][dset_key] = {}
            dict_order_y_x[dset_type][dset_key] = dset_vars
    return dict_order_y_x
# -------------------------------------------------------------------------------------
