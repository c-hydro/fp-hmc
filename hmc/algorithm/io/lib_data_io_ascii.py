"""
Class Features

Name:          lib_data_io_ascii
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20200401'
Version:       '3.0.0'
"""

#######################################################################################
# Libraries
import logging
import os
import itertools

from abc import ABC
from copy import deepcopy

import numpy as np
import pandas as pd

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
# import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Super class to wrap dataframe behaviour
class DFrameCustom(pd.DataFrame, ABC):
    pass
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read state point file
def read_state_point(file_name, file_time, var_name='state', file_time_start=None, file_time_end=None, file_time_frequency='H',
                     file_columns_type=None, file_columns_name=None, list_columns_excluded=None):

    if file_columns_type is None:
        file_columns_type = {0: 'dset'}
    file_type = list(file_columns_type.values())

    if file_time_start == file_time_end:
        time_range = pd.DatetimeIndex([file_time_end])
        time_n = time_range.__len__()
    else:
        log_stream.error(' ===> Time steps conditions are not supported!')
        raise NotImplementedError('Case not implemented')

    if isinstance(file_name, list):
        file_name = file_name[0]

    dframe_summary = {}
    if os.path.exists(file_name):
        file_table = pd.read_table(file_name, header=None)
        file_row_values = file_table.values.tolist()

        id_tot = 0
        data_obj = {}
        for name_id, name_step in enumerate(file_columns_name):
            for type_id, type_step in enumerate(file_type):

                file_row_tmp = file_row_values[id_tot]
                file_row_step = file_row_tmp[0].strip().split()

                if type_step not in list_columns_excluded:
                    if type_step == 'dam_index':
                        row_data = [int(elem) for elem in file_row_step]
                    else:
                        row_data = [float(elem) for elem in file_row_step]

                    if type_step not in list(data_obj.keys()):
                        data_obj[type_step] = {}
                    data_obj[type_step][name_step] = row_data

                id_tot += 1

        for var_id, (var_key, var_ts) in enumerate(data_obj.items()):
            for var_pivot, var_data in var_ts.items():

                dframe_pnt = DFrameCustom(index=time_range)
                dframe_pnt.name = var_name

                dframe_tmp = pd.DataFrame(index=time_range, data=var_data, columns=[var_pivot])
                dframe_tmp.index.name = 'Time'
                series_filled = dframe_tmp.iloc[:, 0]
                dframe_pnt[var_pivot] = series_filled

                if var_key not in list(dframe_summary.keys()):
                    dframe_summary[var_key] = dframe_pnt
                else:
                    dframe_tmp = dframe_summary[var_key]
                    dframe_join = dframe_tmp.join(dframe_pnt, how='right')
                    dframe_join.name = var_name
                    dframe_summary[var_key] = dframe_join
    else:
        dframe_summary = None

    return dframe_summary
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read outcome point file
def read_outcome_point(file_name, file_time, file_columns=None, file_map=None, file_ancillary=None):

    if file_columns is None:
        file_columns = {0: 'dset'}

    if not isinstance(file_name, list):
        file_name = [file_name]

    data_obj = {}
    time_step_expected = []
    time_step_exists = []
    for file_n, (file_step, time_step) in enumerate(zip(file_name, file_time)):

        time_step_expected.append(time_step)

        if os.path.exists(file_step):

            file_size = os.path.getsize(file_step)

            if file_size > 0:

                file_table = pd.read_table(file_step, header=None)
                time_step_exists.append(time_step)

                for row_id, row_value in zip(file_table.index, file_table.values):

                    if row_value.__len__() == 1:
                        row_value = row_value[0]
                    else:
                        raise NotImplementedError(' ===> Length list not allowed')

                    if row_id not in list(data_obj.keys()):
                        data_obj[row_id] = [row_value]
                    else:
                        row_tmp = data_obj[row_id]
                        row_tmp.append(row_value)
                        data_obj[row_id] = row_tmp
            else:
                log_stream.warning(' ===> Size of ' + file_step + ' is equal to zero. File is empty.')
                data_obj = None

    if data_obj is not None:
        data_var = {}
        for data_id, (data_ref, data_ts) in enumerate(data_obj.items()):

            if file_ancillary is not None:
                data_name = list(file_ancillary.keys())[data_id]
            else:
                data_name = data_ref

            for tag_columns in file_columns.values():

                if tag_columns not in list(data_var.keys()):
                    data_var[tag_columns] = {}

                data_var[tag_columns][data_name] = {}
                data_var[tag_columns][data_name] = data_ts

        time_n = time_step_expected.__len__()
        var_data_expected = [-9999.0] * time_n

        dframe_summary = {}
        dframe_merged = pd.DataFrame(index=time_step_expected)
        for var_id, (var_key, var_ts) in enumerate(data_var.items()):
            for var_pivot, var_data_defined in var_ts.items():

                if file_map is not None:
                    if var_pivot in list(file_ancillary.keys()):
                        for map_key, map_fields in file_map.items():
                            var_data_ancillary = file_ancillary[var_pivot][map_key]
                            var_lim_min = map_fields['limits'][0]
                            var_lim_max = map_fields['limits'][1]
                            if map_fields['type'] == 'constant':
                                assert np.isscalar(var_data_ancillary)
                            else:
                                log_stream.error(' ===> Map key "' + map_key + '" type is not allowed.')
                                raise NotImplementedError('Case not implemented yet')

                            if map_key == 'section_baseflow':
                                var_data_tmp = deepcopy(var_data_defined)
                                var_data_defined = []
                                for value_tmp in var_data_tmp:
                                    value_step = value_tmp + var_data_ancillary
                                    if (var_lim_min is not None) and (value_step < var_lim_min):
                                        value_step = value_tmp
                                    if (var_lim_max is not None) and (value_step > var_lim_max):
                                        value_step = var_lim_max
                                    var_data_defined.append(value_step)

                dframe_expected = pd.DataFrame(index=time_step_expected, data=var_data_expected, columns=[var_pivot])
                dframe_expected.index.name = 'Time'

                dframe_point_tmp = pd.DataFrame(index=time_step_exists, data=var_data_defined, columns=[var_pivot])
                dframe_point_tmp.index.name = 'Time'

                dframe_expected.update(dframe_point_tmp)
                series_filled = dframe_expected.iloc[:, 0]
                dframe_merged[var_pivot] = series_filled

            dframe_summary[var_key] = deepcopy(dframe_merged)

    else:
        dframe_summary = None

    return dframe_summary

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data point file
def read_data_point(file_name, file_time, file_columns=None, file_lut=None, file_ancillary=None,
                    select_columns=None):

    if file_columns is None:
        file_columns = {0: 'ref', 1: 'dset'}
    if select_columns is None:
        select_columns = list(file_columns.values())

    if not isinstance(file_name, list):
        file_name = [file_name]

    idxs_lut = []
    if file_lut is not None:

        list_lut = []
        [list_lut.extend([k, v]) for k, v in file_lut.items()]

        for step_lut in list_lut:
            list_columns = list(file_columns.values())
            if step_lut in list_columns:
                idx_lut = list_columns.index(step_lut)
                idxs_lut.append(idx_lut)

    data_lut, data_obj = {}, {}
    time_step_expected, time_step_exists = [], []
    for file_n, (file_step, time_step) in enumerate(zip(file_name, file_time)):

        time_step_expected.append(time_step)

        if os.path.exists(file_step):

            file_table = pd.read_table(file_step, header=None)
            time_step_exists.append(time_step)

            id_nan = 0
            for file_idx, file_array in zip(file_table.index, file_table.values):
                file_row = file_array.tolist()[0]

                if isinstance(file_row, str):
                    file_row_strip = file_row.strip()
                    file_row_split = file_row_strip.split()

                else:
                    log_stream.error(' ===> Data ascii point format is not allowed')
                    raise NotImplementedError(' ===> Case not implemented yet')

                file_row_lut = deepcopy(file_row_split)
                for row_n, row_value in enumerate(file_row_split):

                    col_type = file_columns[row_n]
                    if col_type == 'ref':
                        row_value = float(row_value)

                        if row_value < 0:
                            string_no_code = 'no_code_{}'.format(id_nan)
                            # string_no_code = 'no_code_{}'.format(file_idx)
                            id_nan += 1
                            row_value_upd = string_no_code
                            # update codes to lut variable(s)
                            file_row_lut[row_n] = row_value_upd
                        else:
                            row_value_upd = str(int(row_value))
                    else:
                        row_value_upd = row_value

                    if col_type == 'ref':
                        value_ref = row_value_upd
                        if value_ref not in list(data_obj.keys()):
                            data_obj[value_ref] = {}
                    else:

                        if col_type in select_columns:
                            if isinstance(row_value_upd, str):

                                try:
                                    row_value_upd = float(row_value_upd)
                                except BaseException as exp_obj:
                                    row_value_upd = row_value_upd
                                    log_stream.warning(' ===> Value ' + str(row_value_upd) +
                                                       ' is not cast to float. Check your time-series for errors'
                                                       ' Exception ' + str(exp_obj))

                            value_dset = row_value_upd
                            if col_type not in list(data_obj[value_ref].keys()):
                                data_obj[value_ref][col_type] = {}
                                data_obj[value_ref][col_type] = [value_dset]
                            else:
                                row_tmp = data_obj[value_ref][col_type]
                                row_tmp.append(value_dset)
                                data_obj[value_ref][col_type] = row_tmp

                if file_lut is not None:
                    key_lut = file_row_lut[idxs_lut[0]]
                    value_lut = file_row_lut[idxs_lut[1]]

                    if isinstance(key_lut, str):
                        key_lut = key_lut.lower()

                    if key_lut not in list(data_lut.keys()):
                        data_lut[key_lut] = value_lut

    n_obs = data_obj.__len__()
    if file_ancillary is not None:
        n_anc = file_ancillary.__len__()
    else:
        n_anc = 0

    if n_obs < n_anc:
        file_keys_sel = file_ancillary[0: n_obs]
    elif n_obs == n_anc:
        file_keys_sel = file_ancillary
    elif n_obs > n_anc:
        data_obj = dict(itertools.islice(data_obj.items(), n_anc))
        file_keys_sel = file_ancillary
    else:
        log_stream.error(' ===> Data ascii time-series length case is not allowed')
        raise NotImplementedError('Case not implemented yet')

    if isinstance(file_keys_sel[0], str):
        file_keys_lut = [elem.lower() for elem in file_keys_sel]
    else:
        file_keys_lut = deepcopy(file_keys_sel)

    # Data expected
    time_n = time_step_expected.__len__()
    var_data_expected = [-9999.0] * time_n

    data_list, data_var = [], {}
    for id_key, (data_key, lut_key) in enumerate(zip(file_keys_sel, file_keys_lut)):

        if data_lut:
            if (lut_key is not None) and (lut_key in list(data_lut.keys())):
                tag_lut = data_lut[lut_key]
            elif (lut_key is not None) and (lut_key not in list(data_lut.keys())):
                tag_lut = 'NA'
                log_stream.warning(' ===> Data ascii time-series for point "' + data_key +
                                   '" not found due to the lacking of values in the dynamic files')
            else:
                tag_lut = None
                log_stream.warning(' ===> Data ascii time-series for point "' + data_key +
                                   '" not found due to the mismatch between the static file and the dynamic files')
        else:
            tag_lut = list(data_obj.keys())[id_key]

        if tag_lut:

            if tag_lut in list(data_obj.keys()):
                data_value = data_obj[tag_lut]

            elif (tag_lut != 'NA') and (tag_lut not in list(data_obj.keys())):
                log_stream.warning(' ===> Code for point "' + data_key + '" not found in the dynamic file')
                data_value = {}
                for tag_columns in file_columns.values():
                    if tag_columns != 'ref':
                        data_value[tag_columns] = deepcopy(var_data_expected)

            elif (tag_lut == 'NA') and (tag_lut not in list(data_obj.keys())):
                log_stream.warning(' ===> Code for point "' + data_key + '" is undefined')
                data_value = {}
                for tag_columns in file_columns.values():
                    if tag_columns != 'ref':
                        data_value[tag_columns] = deepcopy(var_data_expected)
            else:
                log_stream.error(' ===> Time-series datasets fails in unknown error')
                raise RuntimeError('Check the routine to fix the bug.')

            for tag_columns in file_columns.values():
                if tag_columns != 'ref':

                    if tag_columns in list(data_value.keys()):
                        data_ts = data_value[tag_columns]

                        if tag_columns not in list(data_var.keys()):
                            data_var[tag_columns] = {}
                        if data_key not in list(data_var[tag_columns].keys()):
                            data_var[tag_columns][data_key] = {}
                            data_var[tag_columns][data_key] = data_ts

                        if data_key not in data_list:
                            data_list.append(data_key)

    dframe_summary = {}
    dframe_merged = pd.DataFrame(index=time_step_expected)
    for var_id, (var_key, var_ts) in enumerate(data_var.items()):
        for var_pivot, var_data_defined in var_ts.items():

            if var_data_defined.__len__() == var_data_expected.__len__():

                dframe_expected = pd.DataFrame(index=time_step_expected, data=var_data_expected, columns=[var_pivot])
                dframe_expected.index.name = 'Time'

                dframe_point_tmp = pd.DataFrame(index=time_step_exists, data=var_data_defined, columns=[var_pivot])
                dframe_point_tmp.index.name = 'Time'

                dframe_expected.update(dframe_point_tmp)
                series_filled = dframe_expected.iloc[:, 0]
                dframe_merged[var_pivot] = series_filled
            else:
                log_stream.error(' ===> Data ascii time-series length is not correct')
                raise IOError(' ===> Time-series defined have not the same length of time-series expected')

        dframe_summary[var_key] = deepcopy(dframe_merged)

    return dframe_summary
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read outcome time-series file
def read_outcome_time_series(file_name, file_time,
                             file_columns_type=None, file_columns_name=None,
                             file_time_start=None, file_time_end=None, file_time_frequency='H', column_sep=';'):

    if file_columns_type is None:
        file_columns_type = {0: 'dset'}
    file_ref = list(file_columns_type.values())[0]

    if column_sep in file_name[0]:
        file_name = file_name[0].split(column_sep)

    data_obj = {file_ref: {}}
    for file_n, (file_step, file_col) in enumerate(zip(file_name, file_columns_name)):

        if os.path.exists(file_step):
            file_table = pd.read_table(file_step, header=None)
            file_column_values = file_table.values.tolist()
            file_row_values = [item for sublist in file_column_values for item in sublist]

            data_obj[file_ref][file_col] = file_row_values

    time_range_expected = pd.date_range(start=file_time_start, end=file_time_end, freq=file_time_frequency)
    time_n_expected = time_range_expected.__len__()
    var_data_expected = [-9999.0] * time_n_expected

    dframe_summary = {}
    dframe_merged = pd.DataFrame(index=time_range_expected)
    for var_id, (var_key, var_ts) in enumerate(data_obj.items()):
        for var_pivot, var_data_dataset in var_ts.items():

            time_n_dataset = var_data_dataset.__len__()

            file_time_dataset = file_time[0]
            time_range_dataset = pd.date_range(start=file_time_dataset,
                                               periods=time_n_dataset, freq=file_time_frequency)

            dframe_dataset = pd.DataFrame(index=time_range_dataset, data=var_data_dataset, columns=[var_pivot])
            dframe_time_start = dframe_dataset.index[0]
            dframe_time_end = dframe_dataset.index[-1]

            var_time_start = time_range_dataset[time_range_dataset == file_time_start][0]
            var_time_end = time_range_dataset[time_range_dataset == file_time_end][0]

            if var_time_start >= dframe_time_start:
                var_time_start_select = var_time_start
            else:
                var_time_start_select = dframe_time_start
            if var_time_end >= dframe_time_end:
                var_time_end_select = dframe_time_end
            else:
                var_time_end_select = var_time_end

            dframe_time_series_filled = dframe_dataset[var_time_start_select: var_time_end_select]
            dframe_time_series_filled.index.name = 'Time'

            series_filled = dframe_time_series_filled.iloc[:, 0]
            dframe_merged[var_pivot] = series_filled

        dframe_summary[var_key] = deepcopy(dframe_merged)

    return dframe_summary
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to read data time-series file
def read_data_time_series(file_name, file_time,
                          file_columns_type=None, file_columns_name=None,
                          file_time_start=None, file_time_end=None, file_time_frequency='H', column_sep=';'):

    if file_columns_type is None:
        file_columns_type = {0: 'dset'}
    file_ref = list(file_columns_type.values())[0]

    if file_columns_name is None:           #add20210607
        file_name[0] = None                 #add20210607

    if file_name[0] is not None:
        if column_sep in file_name[0]:
            file_name = file_name[0].split(column_sep)

        data_obj = {file_ref: {}}
        for file_n, (file_step, file_col) in enumerate(zip(file_name, file_columns_name)):

            if os.path.exists(file_step):
                file_table = pd.read_table(file_step, header=None)
                file_column_values = file_table.values.tolist()
                file_row_values = [item for sublist in file_column_values for item in sublist]

                data_obj[file_ref][file_col] = file_row_values

        time_range_expected = pd.date_range(start=file_time_start, end=file_time_end, freq=file_time_frequency)
        time_n_expected = time_range_expected.__len__()
        var_data_expected = [-9999.0] * time_n_expected

        dframe_summary = {}
        dframe_merged = pd.DataFrame(index=time_range_expected)
        for var_id, (var_key, var_ts) in enumerate(data_obj.items()):
            for var_pivot, var_data_dataset in var_ts.items():

                time_n_dataset = var_data_dataset.__len__()

                file_time_dataset = file_time[0]
                time_range_dataset = pd.date_range(start=file_time_dataset,
                                                   periods=time_n_dataset, freq=file_time_frequency)

                dframe_dataset = pd.DataFrame(index=time_range_dataset, data=var_data_dataset, columns=[var_pivot])
                dframe_time_start = dframe_dataset.index[0]
                dframe_time_end = dframe_dataset.index[-1]

                var_time_start = time_range_dataset[time_range_dataset == file_time_start][0]
                var_time_end = time_range_dataset[time_range_dataset == file_time_end][0]

                if var_time_start >= dframe_time_start:
                    var_time_start_select = var_time_start
                else:
                    var_time_start_select = dframe_time_start
                if var_time_end >= dframe_time_end:
                    var_time_end_select = dframe_time_end
                else:
                    var_time_end_select = var_time_end

                dframe_time_series_filled = dframe_dataset[var_time_start_select: var_time_end_select]
                dframe_time_series_filled.index.name = 'Time'

                series_filled = dframe_time_series_filled.iloc[:, 0]
                dframe_merged[var_pivot] = series_filled

            dframe_summary[var_key] = deepcopy(dframe_merged)

    else:

        dframe_summary = None

    return dframe_summary
# -------------------------------------------------------------------------------------
