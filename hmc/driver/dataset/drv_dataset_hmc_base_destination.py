"""
Class Features

Name:          drv_dataset_hmc_base_destination
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging

import pandas as pd

from copy import deepcopy

from hmc.algorithm.default.lib_default_args import logger_name

from hmc.driver.dataset.drv_dataset_hmc_io_dynamic_outcome import DSetManager as DSetManager_Outcome
from hmc.driver.dataset.drv_dataset_hmc_io_dynamic_outcome import DSetManager as DSetManager_State
from hmc.driver.dataset.drv_dataset_hmc_io_dynamic_summary import DSetManager as DSetManager_Summary

# Log
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to write model datasets
class ModelDestination:

    # -------------------------------------------------------------------------------------
    # Method to initialize class
    def __init__(self,
                 collection_dynamic=None,
                 obj_dataset=None,
                 obj_geo_reference=None,
                 tag_dset_geo='DataGeo',
                 tag_dset_outcome='DataOutcome', tag_dset_state='DataState', tag_dset_summary='DataSummary',
                 template_time=None,
                 template_run_def=None,
                 template_run_ref=None,
                 template_static=None,
                 template_outcome=None,
                 **kwargs):

        self.dset_collections_dynamic = collection_dynamic

        self.dset_obj = obj_dataset
        self.geo_obj = obj_geo_reference

        self.dset_geo = self.dset_obj[tag_dset_geo]
        self.dset_outcome = self.dset_obj[tag_dset_outcome]
        self.dset_state = self.dset_obj[tag_dset_state]
        self.dset_summary = self.dset_obj[tag_dset_summary]

        self.obj_template_time = template_time
        self.obj_template_run_def = template_run_def
        self.obj_template_run_ref = template_run_ref
        self.obj_template_dset_static_ref = template_static
        self.obj_template_dset_outcome_ref = template_outcome

        self.tag_model = 'hmc'
        self.tag_datasets = 'datasets'

        self.writer_outcome = DSetManager_Outcome(
            dset=self.dset_outcome,
            terrain_values=self.geo_obj['values'],
            terrain_geo_x=self.geo_obj['longitude'],
            terrain_geo_y=self.geo_obj['latitude'],
            terrain_transform=self.geo_obj['transform'],
            dset_list_type=['ARCHIVE'],
            model_tag=self.tag_model, datasets_tag=self.tag_datasets, template_time=self.obj_template_time,
            file_compression_mode=True)

        self.vars_outcome_analysis = {'Gridded': ['LST', 'SM'],
                                      'Point': ['Discharge', 'DamV', 'DamL'],
                                      'TimeSeries': None}

        self.writer_state = DSetManager_State(
            dset=self.dset_state,
            terrain_values=self.geo_obj['values'],
            terrain_geo_x=self.geo_obj['longitude'],
            terrain_geo_y=self.geo_obj['latitude'],
            terrain_transform=self.geo_obj['transform'],
            dset_list_type=['ARCHIVE'],
            model_tag=self.tag_model, datasets_tag=self.tag_datasets, template_time=self.obj_template_time,
            file_compression_mode=True)

        self.vars_state_analysis = {'Gridded': None, 'Point': None}

        self.writer_summary = DSetManager_Summary(
            dset=self.dset_summary,
            terrain_values=self.geo_obj['values'],
            terrain_geo_x=self.geo_obj['longitude'],
            terrain_geo_y=self.geo_obj['latitude'],
            terrain_transform=self.geo_obj['transform'],
            template_time=self.obj_template_time,
            file_compression_mode=False)

        self.nan_filled_value = -9998.0
        self.nan_filled_array = -9997.0

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to analyze dynamic outcome/state datasets and model
    def analyze_data_dynamic(self, obj_time_series, obj_time_info, obj_static_datasets,
                             obj_dynamic_datasets, tag_exectype='SIM', tag_datatype='ARCHIVE', tag_datadriver='outcome'):

        # Starting info
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... ')

        if tag_datadriver == 'outcome':
            writer_dataset = self.writer_outcome
        elif tag_datadriver == 'state':
            writer_dataset = self.writer_state
        else:
            log_stream.error(' ===> Destination datasets driver is not allowed')
            raise RuntimeError('Bad definition of datasets driver')
        dset_collections_dynamic_in = self.dset_collections_dynamic

        obj_dset_base = swap_dict_keys(writer_dataset.dset_obj)
        fx_dset_base = swap_dict_keys(writer_dataset.dset_fx)

        dset_collections_dynamic_out = {}
        for (run_key, obj_ts_step), obj_ti_step, obj_dset_step in zip(obj_time_series.items(),
                                                                      obj_time_info.values(),
                                                                      obj_dynamic_datasets.values()):
            # info
            log_stream.info(' -----> Run ' + run_key + ' ... ')

            if (dset_collections_dynamic_in is not None) and (run_key in list(dset_collections_dynamic_in.keys())):
                dset_collections_dynamic_tmp = deepcopy(dset_collections_dynamic_in[run_key])
            else:
                dset_collections_dynamic_tmp = None

            obj_ts_select = obj_ts_step.loc[obj_ts_step['Exec_Type'] == tag_exectype]

            id_ts_tmp = list(set(obj_ts_select['File_Group'].values))
            id_ts_select = [x for x in id_ts_tmp if x == x]

            type_ts_tmp = []
            group_ts_tmp = []
            for type_step, group_step in zip(obj_ts_select['File_Type'].values, obj_ts_select['File_Group'].values):
                if group_step not in group_ts_tmp:
                    group_ts_tmp.append(group_step)
                    type_ts_tmp.append(type_step)
            type_ts_select = [x for x in type_ts_tmp if x == x]

            dset_model_dyn = obj_dset_step[self.tag_model]
            dset_destination_dyn = obj_dset_step[self.tag_datasets]

            dset_model_base = obj_dset_base[self.tag_model]
            dset_destination_base = obj_dset_base[self.tag_datasets]

            fx_destination_base = fx_dset_base[self.tag_datasets]

            if dset_collections_dynamic_tmp is None:
                index_ts_expected = obj_ts_step.index
                values_ts_expected = {'Exec_Type': obj_ts_step['Exec_Type'].values}
                dset_collections_dynamic_tmp = pd.DataFrame(values_ts_expected, index=index_ts_expected)
                dset_collections_dynamic_tmp.index.name = 'time'

            if 'Exec_Type' not in list(dset_collections_dynamic_tmp.columns):
                values_exec_type = obj_ts_step['Exec_Type'].values
                dset_collections_dynamic_tmp['Exec_Type'] = values_exec_type

            for id_ts_step, type_ts_step in zip(id_ts_select, type_ts_select):

                obj_ts_subselect = obj_ts_select.loc[obj_ts_select['File_Group'] == int(id_ts_step)]
                idx_ts_subselect = obj_ts_subselect.index

                start_idx_subselect = idx_ts_subselect[0]
                end_idx_subselect = idx_ts_subselect[-1]

                for file_type in list(dset_destination_dyn.keys()):

                    # Get model datasets
                    dset_model_subset_base = dset_model_base[file_type]

                    # Selection based on type and indexes
                    dset_model_type_dyn = dset_model_dyn[file_type]
                    dset_destination_type_dyn = dset_destination_dyn[file_type]

                    dset_destination_subset_base = dset_destination_base[file_type][tag_datatype]
                    fx_destination_subset_base = fx_destination_base[file_type][tag_datatype]

                    dset_model_subset_dyn = dset_model_type_dyn[start_idx_subselect:end_idx_subselect]
                    dset_destination_subset_dyn = dset_destination_type_dyn[start_idx_subselect:end_idx_subselect]

                    # Outcome datasets operation(s)
                    log_stream.info(' ------> Datasets ' + file_type + ' operations for period ' +
                                    type_ts_step + ' ... ')
                    if fx_destination_subset_base['copy']:
                        writer_dataset.copy_data(dset_model_subset_dyn, dset_destination_subset_dyn)
                        log_stream.info(' ------> Datasets ' + file_type + ' operations for period ' +
                                        type_ts_step + ' ... DONE')
                    elif not fx_destination_subset_base['copy']:
                        log_stream.info(' ------> Datasets ' + file_type + ' operations for period ' +
                                        type_ts_step + ' ... SKIPPED. Copy not activated')
                    else:
                        log_stream.info(' ------> Datasets ' + file_type + ' operations for period ' +
                                        type_ts_step + ' ... FAILED')
                        log_stream.error(' ===> Only copy operations are allowed for outcome datasets')
                        raise RuntimeError('Operation not permitted')

                    # Outcome datasets analysis
                    log_stream.info(' ------> Datasets ' + file_type + ' analysis for period ' +
                                    type_ts_step + ' ... ')
                    if fx_destination_subset_base['analyze']:
                        dset_destination_frame_raw = writer_dataset.collect_data(
                            dset_model_subset_dyn, dset_destination_subset_dyn,
                            dset_model_subset_base, dset_destination_subset_base,
                            dset_static_info=obj_static_datasets,
                            dset_time_info=obj_ti_step,
                            dset_time_start=start_idx_subselect, dset_time_end=end_idx_subselect)

                        # Check collected data
                        if dset_destination_frame_raw[self.tag_datasets] is not None:

                            # Get analysis vars
                            if file_type in list(self.vars_outcome_analysis.keys()):
                                vars_analysis = self.vars_outcome_analysis[file_type]
                            else:
                                vars_analysis = None

                            # Organize data
                            dset_destination_frame_values_def, dset_destination_frame_ts_def = writer_dataset.organize_data(
                                idx_ts_subselect, dset_destination_frame_raw,
                                dset_variable_selected=vars_analysis)

                            # Freeze data
                            dset_collections_dynamic_tmp = writer_dataset.freeze_data(
                                deepcopy(dset_collections_dynamic_tmp), dset_destination_frame_ts_def)

                            # Info
                            log_stream.info(' ------> Datasets ' + file_type + ' analysis for period ' +
                                            type_ts_step + ' ... DONE')
                        else:
                            # Info
                            log_stream.info(' ------> Datasets ' + file_type + ' analysis for period ' +
                                            type_ts_step + ' ... SKIPPED. Datasets are undefined')
                    else:
                        # Info
                        log_stream.info(' ------> Datasets ' + file_type + ' analysis for period ' +
                                        type_ts_step + ' ... SKIPPED. Analysis not activated')

            # Dump data in dictionary
            dset_collections_dynamic_out[run_key] = deepcopy(dset_collections_dynamic_tmp)

            # Dump data in class environment
            if self.dset_collections_dynamic is None:
                self.dset_collections_dynamic = {}
            self.dset_collections_dynamic[run_key] = dset_collections_dynamic_tmp

            # Ending info
            log_stream.info(' -----> Run ' + run_key + ' ... DONE')

        # Ending info
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_datatype + ' ... DONE')
        
        return dset_collections_dynamic_out
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize dynamic outcome/state model and datasets
    def organize_data_dynamic(self, time_series_collections, static_datasets_collections, template_run_filled,
                              tag_exectype='SIM', tag_datadriver='outcome'):

        # Starting information
        log_stream.info(' ----> Organize outcome dynamic datasets ... ')

        if tag_datadriver == 'outcome':
            writer_dataset = self.writer_outcome
        elif tag_datadriver == 'state':
            writer_dataset = self.writer_state
        else:
            log_stream.error(' ===> Destination datasets driver is not allowed')
            raise RuntimeError('Bad definition of datasets driver')

        template_run_ref = self.obj_template_run_ref
        template_outcome_ref = self.obj_template_dset_outcome_ref

        template_run_merge = {**template_run_ref, **template_outcome_ref}

        obj_outcome_datasets = {}
        for (run_key, time_series_step), (template_run_step) in zip(
                time_series_collections.items(), template_run_filled.values()):

            log_stream.info(' -----> Run ' + run_key + ' ... ')

            obj_datasets, obj_model = writer_dataset.collect_filename(
                time_series_step, template_run_merge, template_run_step, tag_exectype=tag_exectype)

            obj_outcome_datasets[run_key] = {}
            obj_outcome_datasets[run_key][self.tag_model] = obj_model
            obj_outcome_datasets[run_key][self.tag_datasets] = obj_datasets

            log_stream.info(' -----> Run ' + run_key + ' ... DONE')

        # Ending information
        log_stream.info(' ----> Organize outcome dynamic datasets ... DONE')

        return obj_outcome_datasets
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to analyze dynamic outcome/state datasets and model
    def analyze_data_summary(self, obj_outcome_datasets, obj_time_series, obj_time_info, obj_static_datasets,
                             obj_dynamic_datasets, obj_dynamic_run, tag_exectype='POST_PROCESSING',
                             tag_datadriver='summary'):

        # Starting information
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_exectype + ' ... ')

        if tag_datadriver == 'summary':
            writer_dataset = self.writer_summary
        else:
            log_stream.error(' ===> Destination datasets driver is not allowed')
            raise RuntimeError('Bad definition of datasets driver')

        dset_collections_dynamic = obj_outcome_datasets
        fx_collections = writer_dataset.dset_fx
        dset_collections_default = writer_dataset.dset_obj
        lut_collections = writer_dataset.dset_lut

        for (run_key, obj_ts_step), obj_ti_step, obj_dset_step in zip(obj_time_series.items(),
                                                                      obj_time_info.values(),
                                                                      obj_dynamic_datasets.values()):
            # info
            log_stream.info(' -----> Run ' + run_key + ' ... ')

            if (dset_collections_dynamic is not None) and (run_key in list(dset_collections_dynamic.keys())):

                dframe_collections = dset_collections_dynamic[run_key]
                dframe_collections = dframe_collections.fillna(self.nan_filled_value)
                file_data = dframe_collections.to_dict()
                file_time = list(file_data['File_Type'].keys())

                obj_static = obj_static_datasets
                obj_time = obj_time_info[run_key]
                obj_filename = obj_dynamic_datasets[run_key]

                obj_run = obj_dynamic_run[run_key]

                for dset_key, dset_values in obj_filename.items():

                    # dset_key = 'TimeSeries'
                    # dset_values = obj_filename[dset_key]

                    # Info
                    log_stream.info(' ------> Datasets ' + dset_key + ' ... ')

                    obj_lut_step = lut_collections[dset_key]
                    obj_fx_step = fx_collections[dset_key]
                    obj_default_step = dset_collections_default[dset_key]

                    for lut_name in obj_lut_step:

                        file_dict_tmp = obj_filename[dset_key].to_dict()

                        log_stream.info(' -------> Dump summary outcome ... ')
                        if lut_name in list(file_dict_tmp.keys()):
                            file_name_tmp = file_dict_tmp[lut_name]
                            file_name_filter = [i for i in file_name_tmp.values() if isinstance(i, str)][0]
                            file_list = file_name_filter.split(writer_dataset.list_sep)
                            file_attrs = obj_default_step[lut_name]

                            if obj_fx_step['dump']:
                                writer_dataset.dump_data(file_list, file_data, file_time,
                                                         file_format=file_attrs['var_format'],
                                                         obj_run=obj_run,
                                                         obj_time=obj_time, obj_static=obj_static,
                                                         no_data=self.nan_filled_array)

                                log_stream.info(' -------> Dump summary outcome ... DONE')
                            else:
                                log_stream.info(' -------> Dump summary outcome ... SKIPPED. Dump not activated')
                        else:
                            log_stream.info(
                                ' -------> Dump summary outcome ... SKIPPED. Datasets undefined and dump not activated')
                    # Info
                    log_stream.info(' ------> Datasets ' + dset_key + ' ... DONE')

                log_stream.info(' -----> Run ' + run_key + ' ... DONE')
            else:
                log_stream.info(' -----> Run ' + run_key + ' ... SKIPPED. Datasets are not defined.')

        # Ending information
        log_stream.info(' ----> Analyze ' + tag_datadriver + ' datasets for datatype ' + tag_exectype + ' ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize summary datasets
    def organize_data_summary(self, time_series_collections, static_datasets_collections, template_run_filled,
                              tag_exectype='POST_PROCESSING', tag_datadriver='summary'):

        # Starting information
        log_stream.info(' ----> Organize summary dynamic datasets ... ')

        if tag_datadriver == 'summary':
            writer_dataset = self.writer_summary
        else:
            log_stream.error(' ===> Destination datasets driver is not allowed')
            raise RuntimeError('Bad definition of datasets driver')

        template_run_ref = self.obj_template_run_ref
        template_outcome_ref = self.obj_template_dset_outcome_ref

        template_run_merge = {**template_run_ref, **template_outcome_ref}

        extra_dict = {
            'Collections': None,
            'TimeSeries':
                {'section_name': static_datasets_collections['section_name_list'],
                 'basin_name': static_datasets_collections['basin_name_list']}
        }

        obj_outcome_datasets = {}
        for (run_key, time_series_step), (template_run_step) in zip(
                time_series_collections.items(), template_run_filled.values()):

            log_stream.info(' -----> Run ' + run_key + ' ... ')

            obj_datasets = writer_dataset.collect_filename(
                time_series_step, template_run_merge, template_run_step, extra_dict=extra_dict,
                tag_exectype=tag_exectype)

            obj_outcome_datasets[run_key] = {}
            obj_outcome_datasets[run_key] = obj_datasets

            log_stream.info(' -----> Run ' + run_key + ' ... DONE')

        # Ending information
        log_stream.info(' ----> Organize summary dynamic datasets ... DONE')

        return obj_outcome_datasets
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

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
