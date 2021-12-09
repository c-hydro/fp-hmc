"""
Library Features:

Name:          lib_io_collections
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20211025'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Libraries
import os
import sys
import logging

from copy import deepcopy
from dateutil.parser import parse

import numpy as np
import pandas as pd
import xarray as xr

# Log
log_stream = logging.getLogger(__name__)
log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)-80s %(filename)s:[%(lineno)-6s - %(funcName)-20s()] '
logging.basicConfig(level=logging.DEBUG, format=log_format)

# Settings
attrs_collections_excluded = ['dam_name', 'plant_name', 'dam_system_name',
                              'basin_name', 'section_name', 'outlet_name',
                              'time_length', 'time_format']
time_format_default = '%Y-%m-%d %H-%M'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to select variable collections
def select_collections_var(dframe_collections, var_name='discharge_simulated'):
    dframe_collections_selected = dframe_collections.loc[:, [var_name in i for i in dframe_collections.columns]]
    return dframe_collections_selected
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to join time series collections
def join_collections_ts(dframe_reference=None, dframe_other=None,
                        time_from=None, time_to=None, time_frequency='H'):

    log_stream.info(' --> Join time series collections ... ')

    if (dframe_reference is not None) or (dframe_other is not None):

        if isinstance(dframe_reference, pd.DataFrame) and isinstance(dframe_other, pd.DataFrame):

            times_reference = dframe_reference.index
            times_other = dframe_other.index

            if (time_from is None) and (time_to is None) and (time_frequency is None):
                time_from = times_reference[0]
                time_to = times_reference[-1]
                time_freq = times_reference.inferred_freq
            elif (time_from is None) and (time_to is None) and (time_frequency is not None):
                time_from = times_reference[0]
                time_to = times_reference[-1]
                time_freq = time_frequency
            elif (time_from is not None) and (time_to is not None) and (time_frequency is not None):
                time_from = pd.Timestamp(time_from)
                time_to = pd.Timestamp(time_to)
                time_freq = time_frequency
            else:
                log_stream.error(' ===> The format of time arguments is not expected.')
                raise NotImplementedError('Case not implemented yet')

            if time_freq is None:
                log_stream.warning(' ===> Time frequency is not initializes. Use default value')
                time_freq = time_frequency

            if time_to < time_from:
                log_stream.error(' ===> TimeTo less than TimeFrom')
                raise IOError('TimeTo must be greater than TimeFrom')

            times_common = pd.date_range(start=time_from, end=time_to, freq=time_freq)
            dframe_common = pd.DataFrame(index=times_common)

            dframe_tmp = deepcopy(dframe_common)
            attrs_reference = dframe_reference.attrs
            dframe_reference_joined = dframe_tmp.join(dframe_reference)
            dframe_reference_joined.attrs = attrs_reference

            dframe_tmp = deepcopy(dframe_common)
            attrs_other = dframe_other.attrs
            dframe_other_joined = dframe_tmp.join(dframe_other)
            dframe_other_joined.attrs = attrs_other

            log_stream.info(' --> Join time series collections ... DONE')
        else:
            log_stream.info(' --> Join time series collections ... FAILED')
            log_stream.error(' ===> Reference and other datasets must be dataframes')
            raise NotImplementedError('Case not implemented yet')
    else:
        log_stream.info(' --> Join time series collections ... FAILED')
        log_stream.warning(' ===> Reference and other datasets must be not None')
        dframe_reference_joined = None
        dframe_other_joined = None

    return dframe_reference_joined, dframe_other_joined
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get time series collections for deterministic and probabilistic run
def organize_collections_ts(
        file_path_tmpl_collections='hmc.collections.{time_stamp}_{ensemble_id}.nc',
        file_dset_tmpl=None, file_vars_tmpl=None):

    log_stream.info(' --> Organize time series collections ... ')

    if file_vars_tmpl is None:
        file_vars_tmpl = {
            'time': 'times',
            'rain': 'Rain:hmc_forcing_datasets:{basin_name}:{section_name}',
            'soil_moisture': 'SM:hmc_outcome_datasets:{basin_name}:{section_name}',
            'discharge_simulated': 'Discharge:section_discharge_sim:{basin_name}:{section_name}',
            'discharge_observed': 'Discharge:section_discharge_obs:{basin_name}:{section_name}'
        }

    if file_dset_tmpl is not None:
        if 'section_name' in list(file_dset_tmpl.keys()):
            section_name = file_dset_tmpl['section_name']
        else:
            log_stream.error(' ===> The "section_name" key must be in the file dataset template')
            raise IOError('Key error')
        if 'basin_name' in list(file_dset_tmpl.keys()):
            basin_name = file_dset_tmpl['basin_name']
        else:
            log_stream.error(' ===> The "basin_name" key must be in the file dataset template')
            raise IOError('Key error')
        if 'ensemble_n' in list(file_dset_tmpl.keys()):
            ensemble_n = file_dset_tmpl['ensemble_n']
        else:
            log_stream.error('The "ensemble_n" key must be in the file dataset template')
            raise IOError('Key error')
        if 'time_reference' in list(file_dset_tmpl.keys()):
            time_reference = file_dset_tmpl['time_reference']
        else:
            log_stream.error('The "time" key must be in the file dataset template')
            raise IOError('Key error')

    else:
        log_stream.error('The "file_dset_template" must be defined by "section_name", "ensemble_n" and "time" keys.')
        raise IOError('Object file template not defined')

    if isinstance(time_reference, str):
        time_reference = pd.Timestamp(time_reference)
        time_reference = time_reference.strftime(format='%Y%m%d%H%M')
    else:
        log_stream.error('Object "time" must be in string format')
        raise NotImplementedError('Case not implemented yet')

    if ensemble_n is None:
        run_group = ['deterministic']
    else:
        ensemble_range = list(np.arange(1, ensemble_n + 1, 1))
        run_group = ['{:03}'.format(ensemble_id) for ensemble_id in ensemble_range]
        np.arange(1, ensemble_n)

    folder_name_tmpl_collections, file_name_tmpl_collections = os.path.split(file_path_tmpl_collections)

    ts_time = None
    ts_dict = None
    attrs_dict = None
    for run_step in run_group:

        tags_obj = {'section_name': section_name, 'basin_name': basin_name,
                    'ensemble_id': run_step, 'time_reference': time_reference}

        folder_name_step = folder_name_tmpl_collections.format(**tags_obj)
        file_name_step = file_name_tmpl_collections.format(**tags_obj)
        file_path_step = os.path.join(folder_name_step, file_name_step)

        file_tag_step = os.path.split(file_path_step)[1]

        log_stream.info(' ---> Get collections file "' + file_tag_step + '" ... ')

        if os.path.exists(file_path_step):

            file_dset = xr.open_dataset(file_path_step)

            for var_key, var_name in file_vars_tmpl.items():

                if (var_key == 'time') and (ts_time is None):

                    var_name = file_vars_tmpl['time']
                    ts_time = file_dset[var_name].values
                    ts_time = pd.DatetimeIndex(ts_time)

                    if ts_dict is None:
                        ts_dict = {var_key: ts_time}
                    elif var_key not in list(ts_dict.keys()):
                        ts_dict[var_key] = ts_time

                elif var_key != 'time':

                    var_name = var_name.format(**tags_obj)
                    var_ts = file_dset[var_name].values
                    var_attrs = file_dset.attrs
                    var_ts[var_ts < 0.0] = np.nan

                    if ts_dict is None:
                        ts_dict = {var_key: var_ts}
                    elif var_key not in list(ts_dict.keys()):
                        ts_dict[var_key] = var_ts
                    else:
                        var_tmp = ts_dict[var_key]
                        var_tmp = np.vstack([var_tmp, var_ts])
                        ts_dict[var_key] = var_tmp

                    tmp_attrs = deepcopy(var_attrs)
                    for attr_key, attr_value in tmp_attrs.items():
                        if attr_key in attrs_collections_excluded:
                            var_attrs.pop(attr_key)

                    if attrs_dict is None:
                        attrs_dict = deepcopy(var_attrs)
                    else:
                        for attr_key, attr_value in var_attrs.items():
                            if attr_key in list(attrs_dict.keys()):
                                tmp_value = attrs_dict[attr_key]
                                if isinstance(tmp_value, str):
                                    if tmp_value != attr_value:
                                        tmp_list = [tmp_value, attr_value]
                                        attrs_dict[attr_key] = tmp_list
                                elif isinstance(tmp_value, list):
                                    if attr_value not in tmp_value:
                                        tmp_value.append(attr_value)
                                elif isinstance(tmp_value, (float, int, np.int64)):
                                    if tmp_value != attr_value:
                                        log_stream.warning(' ===> Attribute values is unexpected. '
                                                           'Value differs with the stored one')
                                else:
                                    log_stream.warning(' ===> Attribute format is unexpected.')
                            else:
                                attrs_dict[attr_key] = attr_value

            log_stream.info(' ---> Get collections file "' + file_tag_step + '" ... DONE')
        else:
            log_stream.info(' ---> Get collections file "' + file_tag_step + '" ... FAILED')
            log_stream.warning(' ===> File not found')

    if (attrs_dict is not None) and (file_dset_tmpl is not None):
        attrs_dict = {**file_dset_tmpl, **attrs_dict}

        for attr_key, attr_value in attrs_dict.items():
            if isinstance(attr_value, str):
                try:
                    time_value = pd.Timestamp(attr_value)
                    time_string = time_value.strftime(format=time_format_default)
                    attrs_dict[attr_key] = time_string
                except BaseException as base_exp:
                    pass

    else:
        log_stream.warning(' ===> Attribute object is not correctly defined.  Some fields could be not available')

    log_stream.info(' ---> Create collections dataframe ... ')
    if ts_dict is not None:
        ts_dframe_collections = None
        for ts_key, ts_values in ts_dict.items():
            if ts_key != 'time':

                if ts_values.ndim == 1:
                    ts_data = ts_values
                    ts_columns = [ts_key]
                else:
                    ts_data = np.transpose(ts_values)
                    ts_n = ts_data.shape[1]
                    ts_range = list(np.arange(1, ts_n + 1, 1))
                    ts_columns = ['{:}_{:03}'.format(ts_key, ts_id) for ts_id in ts_range]

                ts_dframe_tmp = pd.DataFrame(index=ts_time, data=ts_data, columns=ts_columns)

                if ts_dframe_collections is None:
                    ts_dframe_collections = deepcopy(ts_dframe_tmp)
                else:
                    ts_dframe_collections = ts_dframe_collections.join(ts_dframe_tmp)

        if attrs_dict is not None:
            ts_dframe_collections.attrs = attrs_dict

        log_stream.info(' ---> Create collections dataframe ... DONE')

    else:
        ts_dframe_collections = None
        log_stream.info(' ---> Create collections dataframe ... FAILED')
        log_stream.warning(' ===> Datasets is null')

    log_stream.info(' --> Organize time series collections ... DONE')

    return ts_dframe_collections
# -------------------------------------------------------------------------------------
