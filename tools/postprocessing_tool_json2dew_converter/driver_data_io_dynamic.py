"""
Class Features

Name:          driver_data_io_dynamic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210126'
Version:       '1.0.0'
"""

######################################################################################
# Library
import logging
import os
import numpy as np
import pandas as pd

from copy import deepcopy

from tools.postprocessing_tool_json2dew_converter.lib_utils_io import read_obj, write_obj
from tools.postprocessing_tool_json2dew_converter.lib_utils_system import fill_tags2string, make_folder
from tools.postprocessing_tool_json2dew_converter.lib_info_args import time_format_algorithm
from tools.postprocessing_tool_json2dew_converter.lib_data_io_json import read_file_ts_hydrograph
from tools.postprocessing_tool_json2dew_converter.lib_data_io_dewetra import prepare_info_dewetra_hydrograph,\
    write_file_dewetra_hydrograph

# Debug
# import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverDynamic
class DriverDynamic:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_now, time_run, src_dict, anc_dict, dest_dict, static_data_collection,
                 alg_ancillary=None, alg_template_tags=None,
                 tag_section_data='section_data', tag_section_name='section_name', tag_basin_name='section_domain',
                 flag_cleaning_dynamic_ancillary=True, flag_cleaning_dynamic_data=True, flag_cleaning_dynamic_tmp=True):

        self.time_now = time_now
        self.time_run = time_run
        self.tag_section_data = tag_section_data
        self.tag_section_name = tag_section_name
        self.tag_basin_name = tag_basin_name
        self.alg_ancillary = alg_ancillary
        self.alg_template_tags = alg_template_tags

        self.section_data_collection = static_data_collection[self.tag_section_data]

        self.file_name_tag = 'file_name'
        self.folder_name_tag = 'folder_name'

        self.domain_name = self.alg_ancillary['domain_name']
        self.run_name_hmc = self.alg_ancillary['run_name_hmc']
        self.run_name_dew = self.alg_ancillary['run_name_dewetra']
        self.run_type = self.alg_ancillary['run_type']

        self.ensemble_start = self.alg_ancillary['ensemble_start']
        self.ensemble_end = self.alg_ancillary['ensemble_end']
        self.ensemble_step = self.alg_ancillary['ensemble_step']
        self.ensemble_format = self.alg_ancillary['ensemble_format']
        self.ensemble_list, self.run_list = self.collect_ensemble_list()

        self.section_name_list = self.collect_section_list([self.tag_section_name])[self.tag_section_name]
        self.basin_name_list = self.collect_section_list([self.tag_basin_name])[self.tag_basin_name]

        self.folder_name_ts_src = src_dict[self.folder_name_tag]
        self.file_name_ts_src = src_dict[self.file_name_tag]
        self.folder_name_ts_anc = anc_dict[self.folder_name_tag]
        self.file_name_ts_anc = anc_dict[self.file_name_tag]
        self.folder_name_ts_dest = dest_dict[self.folder_name_tag]
        self.file_name_ts_dest = dest_dict[self.file_name_tag]

        self.section_tag_list = []
        self.file_path_collections_src = {}
        self.file_path_collections_anc = {}
        self.file_path_collections_dest = {}
        for section_name, basin_name in zip(self.section_name_list, self.basin_name_list):

            section_tag_step = ':'.join([basin_name, section_name])

            file_path_ts_src = self.define_file_timeseries(
                self.time_run, self.folder_name_ts_src, self.file_name_ts_src, file_ensemble_list=None,
                file_extra_args={'section_name': section_name, 'basin_name': basin_name,
                                 'run_name_hmc': self.run_name_hmc})

            file_path_ts_anc = self.define_file_timeseries(
                self.time_run, self.folder_name_ts_anc, self.file_name_ts_anc, file_ensemble_list=None,
                file_extra_args={'section_name': section_name, 'basin_name': basin_name,
                                 'run_name_hmc': self.run_name_hmc})

            file_path_ts_dest = self.define_file_timeseries(
                self.time_run, self.folder_name_ts_dest, self.file_name_ts_dest, file_ensemble_list=None,
                file_extra_args={'section_name': section_name, 'basin_name': basin_name,
                                 'run_name_hmc': self.run_name_hmc})

            self.file_path_collections_src[section_tag_step] = file_path_ts_src
            self.file_path_collections_anc[section_tag_step] = file_path_ts_anc
            self.file_path_collections_dest[section_tag_step] = file_path_ts_dest
            self.section_tag_list.append(section_tag_step)

        self.flag_cleaning_dynamic_ancillary = flag_cleaning_dynamic_ancillary
        self.flag_cleaning_dynamic_data = flag_cleaning_dynamic_data
        self.flag_cleaning_dynamic_tmp = flag_cleaning_dynamic_tmp

        self.ts_time_format = time_format_algorithm

        self.ts_nodata = -9997.0

        self.tag_ts_time = 'time_period'
        self.tag_ts_observed = 'time_series_discharge_observed'
        self.tag_ts_simulated_single_run = 'time_series_discharge_simulated'
        self.tag_ts_simulated_multi_run = 'time_series_discharge_simulated_{:03d}'

        self.tag_run_var = 'run_var'
        self.tag_run_mode = 'run_mode'
        self.tag_run_ens_start = 'run_ensemble_start'
        self.tag_run_ens_end = 'run_ensemble_end'

        self.str_run_mode = 'probabilistic_ensemble'
        self.str_run_ens_start = str(self.ensemble_start)
        self.str_run_ens_end = str(self.ensemble_end)

        self.tag_ws_observed = 'obs_dframe'
        self.tag_ws_simulated = 'sim_dframe'
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define  filename
    def define_file_timeseries(self, time, folder_name_raw, file_name_raw,
                               file_ensemble_list=None, file_extra_args=None):

        if file_extra_args is None:
            file_extra_args = {}
        if file_ensemble_list is None:
            file_ensemble_list = ['000']

        alg_template_tags = self.alg_template_tags
        domain_name = self.domain_name

        file_path_list = []
        for file_ensemble_step in file_ensemble_list:

            alg_template_values = {'domain_name': domain_name,
                                   'section_name': None,
                                   'basin_name': None,
                                   'run_name_hmc': None,
                                   'run_name_dewetra': None,
                                   'ensemble_name': file_ensemble_step,
                                   'source_sub_path_time': time,
                                   'ancillary_sub_path_time': time,
                                   'destination_sub_path_time': time,
                                   'source_datetime': time,
                                   'ancillary_datetime': time,
                                   'destination_datetime': time}

            alg_template_values = {**alg_template_values, **file_extra_args}

            folder_name_def = fill_tags2string(folder_name_raw, alg_template_tags, alg_template_values)
            file_name_def = fill_tags2string(file_name_raw, alg_template_tags, alg_template_values)
            file_path_def = os.path.join(folder_name_def, file_name_def)

            file_path_list.append(file_path_def)

        return file_path_list

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect section information
    def collect_section_list(self, columns_tag=None):

        if columns_tag is None:
            columns_tag = ['section_domain', 'section_name']

        section_data_collection = self.section_data_collection

        section_dict = {}
        for columns_step in columns_tag:
            section_data_step = section_data_collection[columns_step].values.tolist()
            section_dict[columns_step] = section_data_step
        return section_dict

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute ensemble list
    def collect_ensemble_list(self):

        ens_format = self.ensemble_format

        ens_start = self.ensemble_start
        ens_end = self.ensemble_end + 1
        ens_step = self.ensemble_step

        ens_n = np.arange(ens_start, ens_end, ens_step).tolist()
        run_n = np.arange(1, ens_n.__len__() + 1, 1).tolist()

        run_n_list = []
        ens_n_list = []
        for ens_n_step, run_n_step in zip(ens_n, run_n):
            ens_n_str = ens_format.format(ens_n_step)
            ens_n_list.append(ens_n_str)
            run_n_list.append(run_n_step)
        return ens_n_list, run_n_list
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to clean dynamic tmp
    def clean_dynamic_tmp(self):

        flag_cleaning_tmp = self.flag_cleaning_dynamic_tmp
        file_collections_anc = self.file_path_collections_anc

        if flag_cleaning_tmp:
            for point_key, point_file_list in file_collections_anc.items():
                for point_file_name in point_file_list:
                    if os.path.exists(point_file_name):
                        os.remove(point_file_name)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to dump dynamic data
    def dump_dynamic_data(self):

        time = self.time_run

        file_collections_anc = self.file_path_collections_anc
        file_collections_dest = self.file_path_collections_dest

        flag_cleaning_data = self.flag_cleaning_dynamic_data

        logging.info(' ---> Dump dynamic datasets [' + str(time) + '] ... ')

        for (point_tag, point_file_dest), point_file_anc in zip(
                file_collections_dest.items(), file_collections_anc.values()):

            if isinstance(point_file_dest, list):
                point_file_dest = point_file_dest[0]
            if isinstance(point_file_anc, list):
                point_file_anc = point_file_anc[0]

            if flag_cleaning_data:
                if os.path.exists(point_file_dest):
                    os.remove(point_file_dest)

            logging.info(' ----> Point ' + point_tag + ' ... ')

            if not os.path.exists(point_file_dest):
                if os.path.exists(point_file_anc):

                    ts_obj = read_obj(point_file_anc)

                    ts_dataframe_obs = ts_obj[self.tag_ws_observed]
                    ts_dataframe_sim = ts_obj[self.tag_ws_simulated]

                    ts_attrs = ts_dataframe_obs.attrs
                    ts_dataframe = ts_dataframe_obs.merge(ts_dataframe_sim, left_index=True, right_index=True)
                    ts_dataframe = ts_dataframe.reset_index()

                    ts_data = {}
                    for ts_column in list(ts_dataframe.columns):

                        ts_values = ts_dataframe[ts_column].values
                        if ts_column == self.tag_ts_time:
                            ts_values = pd.DatetimeIndex(ts_values)
                            ts_values = [ts_time.strftime(self.ts_time_format) for ts_time in ts_values]

                        ts_data[ts_column] = ts_values

                    point_data = {**ts_attrs, **ts_data}

                    folder_name_dset, file_name_dset = os.path.split(point_file_dest)
                    make_folder(folder_name_dset)

                    [point_ts_obs, point_ts_mod,
                     time_now, time_from, time_resolution_mins, run_n] = prepare_info_dewetra_hydrograph(point_data)

                    write_file_dewetra_hydrograph(point_file_dest, point_ts_obs, point_ts_mod,
                                                  time_now, time_from, time_resolution_mins,
                                                  run_n=run_n, run_name=self.run_name_dew)

                    logging.info(' ----> Point ' + point_tag + ' ... DONE')

                else:
                    logging.info(' ----> Point ' + point_tag + ' ... SKIPPED. Datasets is null')
            else:
                logging.info(' ----> Point ' + point_tag + ' ... SKIPPED. Datasets already exist')

        logging.info(' ---> Dump dynamic datasets [' + str(time) + '] ... DONE')

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize dynamic data
    def organize_dynamic_data(self):

        time = self.time_run

        ensemble_list = self.ensemble_list
        file_collections_src = self.file_path_collections_src
        file_collections_anc = self.file_path_collections_anc

        tag_ts_time = self.tag_ts_time
        tag_ts_obs = self.tag_ts_observed
        tag_ts_sim_srun = self.tag_ts_simulated_single_run
        tag_ts_sim_mrun = self.tag_ts_simulated_multi_run

        flag_cleaning_ancillary = self.flag_cleaning_dynamic_ancillary

        logging.info(' ---> Organize dynamic datasets [' + str(time) + '] ... ')

        for (point_tag, point_file_src), point_file_anc in zip(
                file_collections_src.items(), file_collections_anc.values()):

            if not isinstance(point_file_src, list):
                point_file_src = [point_file_src]
            if isinstance(point_file_anc, list):
                point_file_anc = point_file_anc[0]

            if point_file_src.__len__() == 1:
                tag_mode_run = ['000']
            elif point_file_src.__len__() > 1:
                tag_mode_run = ensemble_list

            logging.info(' ----> Point ' + point_tag + ' ... ')

            if flag_cleaning_ancillary:
                if os.path.exists(point_file_anc):
                    os.remove(point_file_anc)

            if not os.path.exists(point_file_anc):
                ts_len = None
                ts_collections = None
                ts_attrs = None

                tag_ts_obs_list = []
                tag_ts_sim_list = []
                for mode_step, point_file_step in zip(tag_mode_run, point_file_src):

                    if point_file_src.__len__() == 1:
                        tag_ts_sim_step = tag_ts_sim_srun
                    elif point_file_src.__len__() > 1:
                        tag_ts_sim_step = tag_ts_sim_mrun.format(int(mode_step))
                    else:
                        logging.error(' ===> Expected simulations files are equal to zero')
                        raise NotImplementedError('Case not implemented yet')

                    tag_ts_obs_list.append(tag_ts_obs)
                    tag_ts_sim_list.append(tag_ts_sim_step)

                    columns_obs = None
                    columns_sim = None
                    if os.path.exists(point_file_step):

                        point_ts, point_attrs = read_file_ts_hydrograph(
                            point_file_step,
                            tag_discharge_obs_out=tag_ts_obs, tag_discharge_sim_out=tag_ts_sim_srun)

                        tmp_ts = deepcopy(point_ts)

                        # get time info
                        time_index = tmp_ts.index
                        # get obs info
                        ts_obs = tmp_ts[tag_ts_obs].values

                        if columns_obs is None:
                            columns_obs = [tag_ts_obs]
                        else:
                            columns_obs.extend(tag_ts_obs)
                        columns_obs = sorted(list(set(columns_obs)))

                        # get sim(s) info
                        ts_sim = tmp_ts.drop(columns=[tag_ts_obs]).values

                        columns_tmp = list(tmp_ts.drop(columns=[tag_ts_obs]).columns)
                        if columns_sim is None:
                            columns_sim = columns_tmp
                        else:
                            columns_sim.extend(columns_tmp)
                        columns_sim = sorted(list(set(columns_sim)))

                        if (ts_sim.shape.__len__() == 2) and (ts_sim.shape[1] == 1):
                            ts_sim = ts_sim.reshape([time_index.__len__()])

                        if self.tag_run_var in list(point_attrs.keys()):
                            point_attrs[self.tag_run_var] = ensemble_list
                        if self.tag_run_mode in list(point_attrs.keys()):
                            point_attrs[self.tag_run_mode] = self.str_run_mode

                        if ts_collections is None:
                            ts_collections = {}
                        if ts_len is None:
                            ts_len = ts_sim.__len__()
                        if ts_attrs is None:
                            ts_attrs = point_attrs
                        if tag_ts_obs not in ts_collections:
                            ts_collections[tag_ts_obs] = ts_obs
                        if tag_ts_time not in ts_collections:
                            ts_collections[tag_ts_time] = time_index

                        ts_collections[tag_ts_sim_step] = ts_sim

                    else:
                        logging.warning(' ===> RunStep ' + mode_step + ' is not available.')
                        ts_collections[tag_ts_sim_step] = None

                if ts_collections is not None:

                    for ts_type, ts_data in ts_collections.items():
                        if ts_data is None:
                            ts_data_null = np.zeros(shape=[ts_len])
                            ts_data_null[:] = self.ts_nodata
                            ts_collections[ts_type] = ts_data_null

                    ts_collections_obs = ts_collections[tag_ts_obs]
                    ts_dataframe_obs = pd.DataFrame(data=ts_collections_obs, columns=columns_obs,
                                                    index=ts_collections[tag_ts_time])
                    ts_dataframe_obs.index.name = tag_ts_time
                    ts_dataframe_obs.attrs = ts_attrs

                    ts_collections_sim = {x: v for x, v in ts_collections.items() if x in tag_ts_sim_list}
                    ts_values_sim = list(ts_collections_sim.values())[0]
                    ts_dataframe_sim = pd.DataFrame(data=ts_values_sim, columns=columns_sim,
                                                    index=ts_collections[tag_ts_time])
                    ts_dataframe_sim.index.name = tag_ts_time
                    ts_dataframe_sim.attrs = ts_attrs

                    folder_name_anc, file_name_anc = os.path.split(point_file_anc)
                    make_folder(folder_name_anc)

                    ts_obj = {self.tag_ws_observed: ts_dataframe_obs, self.tag_ws_simulated: ts_dataframe_sim}
                    write_obj(point_file_anc, ts_obj)

                    logging.info(' ----> Point ' + point_tag + ' ... DONE')

                else:
                    logging.info(' ----> Point ' + point_tag + ' ... SKIPPED. Datasets is null')

            else:

                logging.info(' ----> Point ' + point_tag + ' ... SKIPPED. Datasets already exist')

        logging.info(' ---> Organize dynamic datasets [' + str(time) + '] ... DONE')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
