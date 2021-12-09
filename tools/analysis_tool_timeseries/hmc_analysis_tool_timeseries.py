"""
Library Features:

Name:          hmc_analysis_tool_timeseries
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20211028'
Version:       '1.0.0'
"""

#######################################################################################
import logging
import os
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd

from copy import deepcopy


from lib_io_collections import organize_collections_ts, join_collections_ts, select_collections_var
from lib_data_geo_shapefile import read_data_section, find_data_section
from lib_utils_io import read_obj, write_obj
from lib_utils_system import make_folder
from lib_graph_ts_nwp import plot_ts_discharge_nwp_probabilistic

# Log
log_stream = logging.getLogger(__name__)
log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)-80s %(filename)s:[%(lineno)-6s - %(funcName)-20s()] '
logging.basicConfig(level=logging.DEBUG, format=log_format)

# Debug
import matplotlib.pylab as plt
#######################################################################################


# -------------------------------------------------------------------------------------
# Section and domain
section_name = 'BrigliaVolpi'
basin_name = 'Tronto'
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# STATIC SECTIONS SHAPEFILE
folder_name_shp = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/data/data_static/shapefile/"
file_name_shp = "fp_sections_marche.shp"

# Organize section dataframe
file_path_shp = os.path.join(folder_name_shp, file_name_shp)
dframe_sections = read_data_section(file_path_shp)
attrs_section = find_data_section(dframe_sections, section_name=section_name, basin_name=basin_name)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# WEATHER STATIONS
folder_name_tmpl = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/weather_stations_realtime/2021/10/15/00/collections/"
file_name_tmpl = "hmc.collections.{time_reference}.nc"

folder_name_ws = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/weather_stations_realtime/2021/10/15/00/collections//"
file_name_ws = "hmc.collections.weather_stations.202110150000.workspace8"

attrs_dset = {
    "time_reference": '2021-10-15 00:00',
    "ensemble_n": None,
    "run_description": "weather stations",
}

attrs_vars = {
    'time': 'times',
    'rain': 'Rain:hmc_forcing_datasets:{basin_name}:{section_name}',
    'soil_moisture': 'SM:hmc_outcome_datasets:{basin_name}:{section_name}',
    'discharge_simulated': 'Discharge:section_discharge_sim:{basin_name}:{section_name}',
    'discharge_observed': 'Discharge:section_discharge_obs:{basin_name}:{section_name}'
}

file_path_collections = os.path.join(folder_name_tmpl, file_name_tmpl)
file_path_ws = os.path.join(folder_name_ws, file_name_ws)

attrs_dset = {**attrs_dset, **attrs_section}
if not os.path.exists(file_path_ws):
    ts_collections_ws_raw = organize_collections_ts(
        file_path_tmpl_collections=file_path_collections, file_dset_tmpl=attrs_dset, file_vars_tmpl=attrs_vars)

    make_folder(folder_name_ws)
    write_obj(file_path_ws, ts_collections_ws_raw)
else:
    ts_collections_ws_raw = read_obj(file_path_ws)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# NWP DETERMINISTIC LAMI-2I
folder_name_tmpl = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/nwp_lami-2i_realtime/2021/10/07/07/collections/"
file_name_tmpl = "hmc.collections.{time_reference}.nc"

folder_name_ws = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/nwp_lami-2i_realtime/2021/10/07/07/collections/"
file_name_ws = "hmc.collections.nwp_ecmwf0100.202110070700.workspace5"

attrs_dset = {
    "time_reference": '2021-10-07 07:00',
    "ensemble_n": None,
    "run_description": "lami-2i deterministic"
}

attrs_vars = {
    'time': 'times',
    'rain': 'Rain:hmc_forcing_datasets:{basin_name}:{section_name}',
    'soil_moisture': 'SM:hmc_outcome_datasets:{basin_name}:{section_name}',
    'discharge_simulated': 'Discharge:section_discharge_sim:{basin_name}:{section_name}',
    'discharge_observed': 'Discharge:section_discharge_obs:{basin_name}:{section_name}'
}

file_path_collections = os.path.join(folder_name_tmpl, file_name_tmpl)
file_path_ws = os.path.join(folder_name_ws, file_name_ws)

attrs_dset = {**attrs_dset, **attrs_section}
if not os.path.exists(file_path_ws):
    ts_collections_nwp_lami2i_raw = organize_collections_ts(
        file_path_tmpl_collections=file_path_collections, file_dset_tmpl=attrs_dset, file_vars_tmpl=attrs_vars)

    make_folder(folder_name_ws)
    write_obj(file_path_ws, ts_collections_nwp_lami2i_raw)
else:
    ts_collections_nwp_lami2i_raw = read_obj(file_path_ws)

ts_collections_nwp_lami2i_period, ts_collections_ws_period = join_collections_ts(
    dframe_reference=ts_collections_nwp_lami2i_raw, dframe_other=ts_collections_ws_raw)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# NWP DETERMINISTIC
folder_name_tmpl = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/nwp_ecmwf0100_realtime/2021/10/07/07/collections/"
file_name_tmpl = "hmc.collections.{time_reference}.nc"

folder_name_ws = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/nwp_ecmwf0100_realtime/2021/10/07/07/collections/"
file_name_ws = "hmc.collections.nwp_ecmwf0100.202110070700.workspace5"

attrs_dset = {
    "time_reference": '2021-10-07 07:00',
    "ensemble_n": None,
    "run_description": "ecmwf deterministic"
}

attrs_vars = {
    'time': 'times',
    'rain': 'Rain:hmc_forcing_datasets:{basin_name}:{section_name}',
    'soil_moisture': 'SM:hmc_outcome_datasets:{basin_name}:{section_name}',
    'discharge_simulated': 'Discharge:section_discharge_sim:{basin_name}:{section_name}',
    'discharge_observed': 'Discharge:section_discharge_obs:{basin_name}:{section_name}'
}

file_path_collections = os.path.join(folder_name_tmpl, file_name_tmpl)
file_path_ws = os.path.join(folder_name_ws, file_name_ws)

attrs_dset = {**attrs_dset, **attrs_section}
if not os.path.exists(file_path_ws):
    ts_collections_nwp_raw = organize_collections_ts(
        file_path_tmpl_collections=file_path_collections, file_dset_tmpl=attrs_dset, file_vars_tmpl=attrs_vars)

    make_folder(folder_name_ws)
    write_obj(file_path_ws, ts_collections_nwp_raw)
else:
    ts_collections_nwp_raw = read_obj(file_path_ws)

ts_collections_nwp_period, ts_collections_ws_period = join_collections_ts(
    dframe_reference=ts_collections_nwp_raw, dframe_other=ts_collections_ws_raw)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# NWP PROBABILISTIC LAMI-2I
folder_name_tmpl = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/rfarm_lami-2i_realtime/2021/10/07/07/probabilistic_ensemble/collections/"
file_name_tmpl = "hmc.collections.{time_reference}_{ensemble_id}.nc"

folder_name_ws = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/rfarm_lami-2i_realtime/2021/10/07/07/probabilistic_ensemble/collections/"
file_name_ws = "hmc.collections.rfarm_lami2i.202110070700.workspace11"

attrs_dset = {
    "time_reference": '2021-10-07 07:00',
    "ensemble_n": 30,
    "run_description": "ecmwf probabilistic"
}

attrs_vars = {
    'time': 'times',
    'rain': 'Rain:hmc_forcing_datasets:{basin_name}:{section_name}',
    'soil_moisture': 'SM:hmc_outcome_datasets:{basin_name}:{section_name}',
    'discharge_simulated': 'Discharge:section_discharge_sim:{basin_name}:{section_name}',
    'discharge_observed': 'Discharge:section_discharge_obs:{basin_name}:{section_name}'
}

file_path_collections = os.path.join(folder_name_tmpl, file_name_tmpl)
file_path_ws = os.path.join(folder_name_ws, file_name_ws)

attrs_dset = {**attrs_dset, **attrs_section}
if not os.path.exists(file_path_ws):
    ts_collections_rfarm_lami2i_raw = organize_collections_ts(
        file_path_tmpl_collections=file_path_collections, file_dset_tmpl=attrs_dset, file_vars_tmpl=attrs_vars)

    make_folder(folder_name_ws)
    write_obj(file_path_ws, ts_collections_rfarm_lami2i_raw)
else:
    ts_collections_rfarm_lami2i_raw = read_obj(file_path_ws)

ts_collections_rfarm_lami2i_period = join_collections_ts(
    dframe_reference=ts_collections_nwp_raw,
    dframe_other=ts_collections_rfarm_lami2i_raw)[1]
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# NWP PROBABILISTIC ECMWF0100
folder_name_tmpl = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/rfarm_ecmwf0100_realtime/2021/10/07/07/probabilistic_ensemble/collections/"
file_name_tmpl = "hmc.collections.{time_reference}_{ensemble_id}.nc"

folder_name_ws = "/home/fabio/Desktop/PyCharm_Workspace/hmc-ws/opchain_marche/archive/rfarm_ecmwf0100_realtime/2021/10/07/07/probabilistic_ensemble/collections/"
file_name_ws = "hmc.collections.rfarm_ecmwf0100.202110070700.workspace11"

attrs_dset = {
    "time_reference": '2021-10-07 07:00',
    "ensemble_n": 30,
    "run_description": "ecmwf probabilistic"
}

attrs_vars = {
    'time': 'times',
    'rain': 'Rain:hmc_forcing_datasets:{basin_name}:{section_name}',
    'soil_moisture': 'SM:hmc_outcome_datasets:{basin_name}:{section_name}',
    'discharge_simulated': 'Discharge:section_discharge_sim:{basin_name}:{section_name}',
    'discharge_observed': 'Discharge:section_discharge_obs:{basin_name}:{section_name}'
}

file_path_collections = os.path.join(folder_name_tmpl, file_name_tmpl)
file_path_ws = os.path.join(folder_name_ws, file_name_ws)

attrs_dset = {**attrs_dset, **attrs_section}
if not os.path.exists(file_path_ws):
    ts_collections_rfarm_raw = organize_collections_ts(
        file_path_tmpl_collections=file_path_collections, file_dset_tmpl=attrs_dset, file_vars_tmpl=attrs_vars)

    make_folder(folder_name_ws)
    write_obj(file_path_ws, ts_collections_rfarm_raw)
else:
    ts_collections_rfarm_raw = read_obj(file_path_ws)

ts_collections_rfarm_period = join_collections_ts(
    dframe_reference=ts_collections_nwp_raw,
    dframe_other=ts_collections_rfarm_raw)[1]
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Select variable(s)
ts_rain_ws_period = select_collections_var(ts_collections_ws_period, 'rain')
ts_discharge_simulated_ws_period = select_collections_var(ts_collections_ws_period, 'discharge_simulated')
ts_discharge_observed_ws_period = select_collections_var(ts_collections_ws_period, 'discharge_observed')
ts_sm_ws_period = select_collections_var(ts_collections_ws_period, 'soil_moisture')

ts_rain_nwp_lami2i_period = select_collections_var(ts_collections_nwp_lami2i_period, 'rain')
ts_discharge_simulated_nwp_lami2i_period = select_collections_var(ts_collections_nwp_lami2i_period, 'discharge_simulated')
ts_sm_nwp_lami2i_period = select_collections_var(ts_collections_nwp_lami2i_period, 'soil_moisture')

ts_rain_nwp_period = select_collections_var(ts_collections_nwp_period, 'rain')
ts_discharge_simulated_nwp_period = select_collections_var(ts_collections_nwp_period, 'discharge_simulated')
ts_sm_nwp_period = select_collections_var(ts_collections_nwp_period, 'soil_moisture')

ts_rain_rfarm_lami2i_period = select_collections_var(ts_collections_rfarm_lami2i_period, 'rain')
ts_discharge_simulated_rfarm_lami2i_period = select_collections_var(ts_collections_rfarm_lami2i_period, 'discharge_simulated')
ts_sm_rfarm_lami2i_period = select_collections_var(ts_collections_rfarm_lami2i_period, 'soil_moisture')

ts_rain_rfarm_period = select_collections_var(ts_collections_rfarm_period, 'rain')
ts_discharge_simulated_rfarm_period = select_collections_var(ts_collections_rfarm_period, 'discharge_simulated')
ts_sm_rfarm_period = select_collections_var(ts_collections_rfarm_period, 'soil_moisture')
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# PLOT LAMI-2I
plot_ts_discharge_nwp_probabilistic(
    None,
    ts_collections_ws_period.attrs,
    ts_collections_nwp_lami2i_period.attrs, ts_collections_rfarm_lami2i_period.attrs,
    ts_rain_ws_period,
    ts_rain_nwp_lami2i_period, ts_rain_rfarm_lami2i_period,
    ts_discharge_simulated_ws_period,
    ts_discharge_simulated_nwp_lami2i_period, ts_discharge_simulated_rfarm_lami2i_period,
    ts_sm_ws_period,
    ts_sm_nwp_lami2i_period, ts_sm_rfarm_lami2i_period,
    ts_discharge_observed_ws_period)

# PLOT ECMWF0100
plot_ts_discharge_nwp_probabilistic(
    None,
    ts_collections_ws_period.attrs,
    ts_collections_nwp_period.attrs, ts_collections_rfarm_period.attrs,
    ts_rain_ws_period,
    ts_rain_nwp_period, ts_rain_rfarm_period,
    ts_discharge_simulated_ws_period,
    ts_discharge_simulated_nwp_period, ts_discharge_simulated_rfarm_period,
    ts_sm_ws_period,
    ts_sm_nwp_period, ts_sm_rfarm_period,
    ts_discharge_observed_ws_period)
# -------------------------------------------------------------------------------------
print('ciao')




