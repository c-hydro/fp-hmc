"""
Class Features

Name:          driver_data_io_dynamic
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210730'
Version:       '1.0.1'
"""
import shutil

######################################################################################
# Library
import logging
import os
import numpy as np

from lib_utils_system import fill_tags2string
from lib_info_args import time_format_algorithm

# Debug
# import matplotlib.pylab as plt
######################################################################################


# -------------------------------------------------------------------------------------
# Class DriverDynamic
class DriverDynamic:

    # -------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, time_now, time_run,
                 src_dict, dst_dict,
                 static_data_collection,
                 alg_ancillary=None, alg_template_tags=None,
                 cleaning_dynamic_source=False, cleaning_dynamic_destination=True):

        # time information
        self.time_now = time_now
        self.time_run = time_run

        # main key(s) information
        self.tag_point_data = 'point_data'
        # sub key(s) information
        self.tag_point_type = 'point_type'
        self.tag_point_variable = 'point_variable'

        # data key(s) information
        self.tag_point_code_ws = 'point_code_ws'
        self.tag_point_code_rs = 'point_code_rs'
        self.tag_point_domain_name = 'point_domain_name'
        self.tag_point_section_name = 'point_section_name'
        self.tag_point_catchment_name = 'point_catchment_name'
        # run key(s) information
        self.tag_run_mode_probabilistic = 'probabilistic'
        self.tag_run_mode_deterministic = 'deterministic'
        # file key(s) information
        self.tag_file_name = 'file_name'
        self.tag_folder_name = 'folder_name'
        self.tag_keys = 'keys'
        # run key(s) information
        self.tag_run_var = 'run_var'
        self.tag_run_mode = 'run_mode'
        self.tag_run_ens_start = 'run_ensemble_start'
        self.tag_run_ens_end = 'run_ensemble_end'

        # object data information
        self.alg_ancillary = alg_ancillary
        self.alg_template_tags = alg_template_tags
        self.point_data_collection = static_data_collection[self.tag_point_data]
        self.point_data_type = static_data_collection[self.tag_point_type]
        self.point_data_variable = static_data_collection[self.tag_point_variable]

        # source, ancillary and destination information
        self.src_domain_name = self.alg_ancillary['source_domain_name']
        self.dst_domain_name = self.alg_ancillary['destination_domain_name']
        self.src_run_name = self.alg_ancillary['source_run_name']
        self.dst_run_name = self.alg_ancillary['destination_run_name']
        self.run_type = self.alg_ancillary['run_type']

        # define run information
        run_mode_probabilistic = self.alg_ancillary[self.tag_run_mode][self.tag_run_mode_probabilistic]
        run_mode_deterministic = self.alg_ancillary[self.tag_run_mode][self.tag_run_mode_deterministic]
        (self.str_run_mode,
         self.ensemble_start, self.ensemble_end, self.ensemble_step, self.ensemble_format) = self.define_run_mode(
            run_mode_deterministic, run_mode_probabilistic, tag_activate='activate')

        self.run_list, self.ensemble_list = self.collect_run_instance()

        # define file(s) information
        self.folder_name_ts_src = src_dict[self.tag_folder_name]
        self.file_name_ts_src = src_dict[self.tag_file_name]
        self.keys_src = src_dict[self.tag_keys]
        self.folder_name_ts_dst = dst_dict[self.tag_folder_name]
        self.file_name_ts_dst = dst_dict[self.tag_file_name]
        self.keys_dst = dst_dict[self.tag_keys]

        self.ts_time_format = time_format_algorithm

        self.tag_ts_time, self.tag_ts_observed, \
            self.tag_ts_simulated_single_run, self.tag_ts_simulated_multi_run = self.define_tag_timeseries()

        self.str_run_ens_start = str(self.ensemble_start)
        self.str_run_ens_end = str(self.ensemble_end)

        self.tag_ws_observed = 'obs_dframe'
        self.tag_ws_simulated = 'sim_dframe'

        self.cleaning_dynamic_source = cleaning_dynamic_source
        self.cleaning_dynamic_destination = cleaning_dynamic_destination
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define run mode
    @staticmethod
    def define_run_mode(run_mode_det, run_mode_prob, tag_activate='activate'):

        if tag_activate in list(run_mode_det.keys()):
            flag_activate_det = run_mode_det[tag_activate]
        else:
            raise IOError('Deterministic mode activate flag not defined. Check your settings file.')
        if tag_activate in list(run_mode_prob.keys()):
            flag_activate_prob = run_mode_prob[tag_activate]
        else:
            raise IOError('Probabilistic mode activate flag not defined. Check your settings file.')

        if flag_activate_det and flag_activate_prob:
            raise IOError('Both deterministic and probabilistic mode are activated. Check your settings file.')
        if (not flag_activate_det) and (not flag_activate_prob):
            raise IOError('Both deterministic and probabilistic mode are not activated. Check your settings file.')

        if flag_activate_det:
            ensemble_start = None
            ensemble_end = None
            ensemble_step = None
            ensemble_format = None
            run_mode_tag = 'deterministic_mode'
        elif flag_activate_prob:
            ensemble_start = run_mode_prob['ensemble_start']
            ensemble_end = run_mode_prob['ensemble_end']
            ensemble_step = run_mode_prob['ensemble_step']
            ensemble_format = run_mode_prob['ensemble_format']
            run_mode_tag = 'probabilistic_mode'
        else:
            raise NotImplementedError('Run mode not implemented yet')

        return run_mode_tag, ensemble_start, ensemble_end, ensemble_step, ensemble_format

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to define tags
    def define_tag_timeseries(self):

        point_type = self.point_data_type
        point_var = self.point_data_variable

        if point_type == 'section':
            if point_var == 'discharge':
                tag_ts_time = 'time_period'
                tag_ts_observed = 'time_series_discharge_observed'
                tag_ts_simulated_single_run = 'time_series_discharge_simulated'
                tag_ts_simulated_multi_run = 'time_series_discharge_simulated_{:03d}'
            else:
                logging.error(' ===> Point variable "' + point_var + '" is not allowed.')
                raise NotImplemented('Case not implemented yet')

        elif point_type == 'dam':
            if point_var == 'dam_volume':
                tag_ts_time = 'time_period'
                tag_ts_observed = 'time_series_dam_volume_observed'
                tag_ts_simulated_single_run = 'time_series_dam_volume_simulated'
                tag_ts_simulated_multi_run = 'time_series_dam_volume_simulated_{:03d}'
            else:
                logging.error(' ===> Point variable "' + point_var + '" is not allowed.')
                raise NotImplemented('Case not implemented yet')
        else:
            logging.error(' ===> Point type "' + point_type + '" is not allowed.')
            raise NotImplemented('Case not implemented yet')

        return tag_ts_time, tag_ts_observed, tag_ts_simulated_single_run, tag_ts_simulated_multi_run

    # -------------------------------------------------------------------------------------
    # Method to define filename
    def define_file_timeseries(self, time,
                               folder_name_raw, file_name_raw,
                               file_ensemble_list=None, file_extra_args=None):

        if file_extra_args is None:
            file_extra_args = {}
        if file_ensemble_list is None:
            file_ensemble_list = [None]

        alg_template_tags = self.alg_template_tags

        file_path_list = []
        for file_ensemble_step in file_ensemble_list:

            alg_template_values = {'point_domain_name': None,
                                   'point_section_name': None,
                                   'point_catchment_name': None,
                                   'source_run_name': None,
                                   'destination_run_name': None,
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
    # Method to collect point information
    @staticmethod
    def collect_point_list(point_data, column_tag=None):

        if column_tag is None:
            column_tag = 'point_catchment_name'

        if column_tag in list(point_data.columns):
            point_data_list = point_data[column_tag].tolist()
        else:
            logging.error(' ===> Column tag "' + column_tag + '" is not allowed.')
            raise RuntimeError('Column tag is not available in point data collection. Check your settings file.')
        return point_data_list

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to collect run instance
    def collect_run_instance(self):

        ens_format = self.ensemble_format

        if ens_format is not None:
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
        else:
            ens_n_list = None
            run_n_list = 1
        return run_n_list, ens_n_list
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to organize dynamic data
    def organize_dynamic_data(self):

        # time information
        time = self.time_run

        # info start method
        logging.info(' ---> Organize dynamic datasets [' + str(time) + '] ... ')

        # datasets static
        point_data_collection = self.point_data_collection
        # keys dynamic
        keys_src = self.keys_src
        keys_dst = self.keys_dst

        # iterate over domain(s) information
        for src_domain_step, dst_domain_step in zip(self.src_domain_name, self.dst_domain_name):

            # info domain start
            logging.info(' ----> Source domain "' + src_domain_step +
                         '" to destination domain "' + dst_domain_step + '" ... ')

            # define domain collection
            point_data_domain = point_data_collection.loc[point_data_collection['point_domain_name'] == src_domain_step]

            # define domain section, catchment and code(s) information
            point_section_name_list = self.collect_point_list(
                point_data_domain, column_tag=self.tag_point_section_name)
            point_catchment_name_list = self.collect_point_list(
                point_data_domain, column_tag=self.tag_point_catchment_name)
            point_code_ws_list = self.collect_point_list(
                point_data_domain, column_tag=self.tag_point_code_ws)
            point_code_rs_list = self.collect_point_list(
                point_data_domain, column_tag=self.tag_point_code_rs)

            # iterate over point(s) information
            src_file_path_collections, dst_file_path_collections = {}, {}
            for point_section_name_step, point_catchment_name_step, point_code_ws_step in zip(
                    point_section_name_list, point_catchment_name_list, point_code_ws_list):

                # define point tag
                point_tag_step = ':'.join([point_catchment_name_step, point_section_name_step])

                # info point start
                logging.info(' -----> Point "' + point_tag_step + '" ... ')

                # define point collection
                point_data_step = point_data_domain.loc[point_data_domain['point_code_ws'] == point_code_ws_step]

                # organize source args
                point_args_src_base = {'source_domain_name': src_domain_step, 'source_run_name': self.src_run_name}
                point_args_src_step = {}
                for key, val in keys_src.items():
                    if val is not None:
                        point_value = point_data_step[val].values[0]
                        point_args_src_step[key] = point_value
                point_args_src_merge = {**point_args_src_base, **point_args_src_step}

                # define source time-series file(s) path
                file_path_ts_src_list = self.define_file_timeseries(
                    self.time_run, self.folder_name_ts_src, self.file_name_ts_src,
                    file_ensemble_list=None,
                    file_extra_args=point_args_src_merge)

                # organize destination args
                point_args_dst_base = {'destination_domain_name': dst_domain_step, 'destination_run_name': self.dst_run_name}
                point_args_dst_step = {}
                for key, val in keys_dst.items():
                    if val is not None:
                        point_value = point_data_step[val].values[0]
                        point_args_dst_step[key] = point_value
                point_args_dst_merge = {**point_args_dst_base, **point_args_dst_step}

                # define destination time-series file(s) path
                file_path_ts_dst_list = self.define_file_timeseries(
                    self.time_run, self.folder_name_ts_dst, self.file_name_ts_dst,
                    file_ensemble_list=None,
                    file_extra_args=point_args_dst_merge)

                # iterate over time-series file(s) path
                for file_path_ts_src_step, file_path_ts_dst_step in zip(file_path_ts_src_list, file_path_ts_dst_list):

                    # info file start
                    logging.info(' ------> Transfer file "' + file_path_ts_src_step + '" to "' +
                                 file_path_ts_dst_step + '" ... ')

                    # check source file availability
                    if os.path.exists(file_path_ts_src_step):

                        # remove dynamic destination
                        if self.cleaning_dynamic_destination:
                            if os.path.exists(file_path_ts_dst_step):
                                os.remove(file_path_ts_dst_step)

                        # create destination folder
                        folder_name_ts_dst, file_name_ts_dst = os.path.split(file_path_ts_dst_step)
                        os.makedirs(folder_name_ts_dst, exist_ok=True)

                        # copy source to destination file
                        shutil.copy2(file_path_ts_src_step, file_path_ts_dst_step)

                        # remove dynamic source
                        if self.cleaning_dynamic_source:
                            if os.path.exists(file_path_ts_src_step):
                                logging.warning(' ===> File source "' + file_path_ts_src_step + '" removed')
                                os.remove(file_path_ts_src_step)

                        # info file end
                        logging.info(' ------> Transfer file "' + file_path_ts_src_step + '" to "' +
                                     file_path_ts_dst_step + '" ... DONE')
                    else:
                        # file check failed
                        logging.warning(' ===> File "' + file_path_ts_src_step + '" not found')

                        # info file end
                        logging.info(' ------> Transfer file "' + file_path_ts_src_step + '" to "' +
                                     file_path_ts_dst_step + '" ... SKIPPED')

                # info point end
                logging.info(' -----> Point "' + point_tag_step + '" ... DONE')

            # info domain end
            logging.info(' ----> Source domain "' + src_domain_step +
                         '" to destination domain "' + dst_domain_step + '" ... DONW')
        # info end method
        logging.info(' ---> Organize dynamic datasets [' + str(time) + '] ... DONE')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
