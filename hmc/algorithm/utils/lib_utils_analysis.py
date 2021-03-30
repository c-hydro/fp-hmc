"""
Library Features:

Name:          lib_utils_analysis
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210324'
Version:       '1.0.0'
"""

#######################################################################################
# Library
import logging
import time

import numpy as np
import pandas as pd
import xarray as xr

from multiprocessing import Pool, cpu_count
from copy import deepcopy

from hmc.algorithm.default.lib_default_args import logger_name

# Log
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt

# Analysis variable default
variable_excluded_default = ['terrain', 'Terrain', 'mask', 'Mask']
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to compute mean values over domain
def compute_domain_mean(var_da, var_dim=None,
                        tag_variable_fields='{var_name}:{domain_name}', template_variable_domain='domain',
                        vars_excluded_list=None):

    if vars_excluded_list is None:
        vars_excluded_list = variable_excluded_default

    if var_dim is None:
        var_dim = ['south_north', 'west_east']
    var_ts_in = var_da.mean(dim=var_dim)
    var_ts_out = update_variable_names(var_ts_in,
                                       vars_excluded_list=vars_excluded_list,
                                       var_domain_fields=tag_variable_fields,
                                       var_domain_template=template_variable_domain)

    return var_ts_out

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to update variable names
def update_variable_names(var_ts_in, vars_excluded_list=None,
                          var_domain_fields='{var_name}:{domain_name}',
                          var_domain_template='generic'):

    if vars_excluded_list is None:
        vars_excluded_list = variable_excluded_default

    variable_list = list(var_ts_in.data_vars)

    variable_lut = {}
    for variable_step_in in variable_list:
        if variable_step_in not in vars_excluded_list:
            tag_dict = {'var_name': variable_step_in, 'domain_name': var_domain_template}
            variable_step_out = var_domain_fields.format(**tag_dict)
            variable_lut[variable_step_in] = variable_step_out

    var_ts_out = var_ts_in.rename(variable_lut)

    return var_ts_out
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to collect results in mp async mode
def organize_outcome(func_obj_out):
    obj_data_out = func_obj_out[1]

    global var_da_section_obj
    if var_da_section_obj is None:
        var_da_section_obj = obj_data_out
    else:
        var_da_section_obj = xr.merge([var_da_section_obj, obj_data_out])

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compute mean values over catchment using mp sync method
def compute_catchment_mean_parallel_async(var_dset, mask_da_obj, mask_var_name='mask',
                                          var_dim_x='west_east', var_dim_y='south_north',
                                          var_coord_x='longitude', var_coord_y='latitude',
                                          cpu_n=40, cpu_max=None,
                                          variable_domain_fields='{var_name}:{domain_name}',
                                          variable_selected_list=None):
    global var_da_section_obj
    global var_dset_global

    log_stream.info(' ---------> Apply method to average time-series in parallel async mode ... ')

    var_dset_global = var_dset

    if variable_selected_list is not None:
        variable_dset_list = list(var_dset_global.data_vars)
        for variable_dset_step in variable_dset_list:
            if variable_dset_step not in variable_selected_list:
                var_dset_global = var_dset_global.drop(variable_dset_step)

    time_start = time.time()
    if var_dim_x is None:
        var_dim_x = 'west_east'
    if var_dim_y is None:
        var_dim_y = 'south_north'

    var_dim_order = [var_dim_y, var_dim_x]

    if cpu_max is None:
        cpu_max = cpu_count() - 1
    if cpu_n > cpu_max:
        log_stream.warning(' ===> Maximum of recommended processes must be less then ' + str(cpu_max))
        log_stream.warning(' ===> Set number of process from ' + str(cpu_n) + ' to ' + str(cpu_max))
        cpu_n = cpu_max

    var_da_section_obj = None
    exec_pool = Pool(cpu_n)
    for mask_key, mask_da in mask_da_obj.items():

        mask_values = np.flipud(mask_da.values)
        mask_geo_y = np.flipud(mask_da['Latitude'].values)
        mask_geo_x = mask_da['Longitude'].values

        if (mask_geo_x.shape.__len__() == 1) and (mask_geo_y.shape.__len__() == 1):
            mask_geo_x_2d, var_geo_y_2d = np.meshgrid(mask_geo_x, mask_geo_y)
        else:
            mask_geo_x_2d = mask_geo_x
            var_geo_y_2d = mask_geo_y

        var_da_mask = xr.DataArray(mask_values, name=mask_var_name,
                                   dims=var_dim_order,
                                   coords={var_coord_x: ([var_dim_y, var_dim_x], mask_geo_x_2d),
                                           var_coord_y: ([var_dim_y, var_dim_x], var_geo_y_2d)})

        func_obj = {'var_mask': var_da_mask, 'var_dim': var_dim_order, 'var_template': variable_domain_fields}
        exec_pool.apply_async(exec_grid2ts, args=(mask_key, func_obj), callback=organize_outcome)

    exec_pool.close()
    exec_pool.join()

    time_end = time.time()
    time_elapsed = time_end - time_start

    log_stream.info(' ----------> Elapsed time: ' + str(np.floor(time_elapsed)) +
                    ' seconds. \n Consider to select a reduced number of variables if process takes a long time.\n')

    log_stream.info(' ---------> Apply method to average time-series in parallel async mode ... DONE')

    return var_da_section_obj

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compute mean values over catchment using mp sync method
def compute_catchment_mean_parallel_sync(var_dset, mask_da_obj, mask_var_name='mask',
                                         var_dim_x='west_east', var_dim_y='south_north',
                                         var_coord_x='longitude', var_coord_y='latitude',
                                         cpu_n=20, cpu_max=20,
                                         variable_domain_fields='{var_name}:{domain_name}',
                                         variable_selected_list=None):

    global var_da_section_obj
    global var_dset_global

    log_stream.info(' ---------> Apply method to average time-series in parallel sync mode ... ')

    var_dset_global = var_dset

    if variable_selected_list is not None:
        variable_dset_list = list(var_dset_global.data_vars)
        for variable_dset_step in variable_dset_list:
            if variable_dset_step not in variable_selected_list:
                var_dset_global = var_dset_global.drop(variable_dset_step)

    time_start = time.time()
    if var_dim_x is None:
        var_dim_x = 'west_east'
    if var_dim_y is None:
        var_dim_y = 'south_north'

    var_dim_order = [var_dim_y, var_dim_x]

    if cpu_max is None:
        cpu_max = cpu_count() - 1
    if cpu_n > cpu_max:
        log_stream.warning(' ===> Maximum of recommended processes must be less then ' + str(cpu_max))
        log_stream.warning(' ===> Set number of process from ' + str(cpu_n) + ' to ' + str(cpu_max))
        cpu_n = cpu_max

    func_obj_list = []
    for mask_key, mask_da in mask_da_obj.items():

        mask_values = np.flipud(mask_da.values)
        mask_geo_y = np.flipud(mask_da['Latitude'].values)
        mask_geo_x = mask_da['Longitude'].values

        if (mask_geo_x.shape.__len__() == 1) and (mask_geo_y.shape.__len__() == 1):
            mask_geo_x_2d, var_geo_y_2d = np.meshgrid(mask_geo_x, mask_geo_y)
        else:
            mask_geo_x_2d = mask_geo_x
            var_geo_y_2d = mask_geo_y

        var_da_mask = xr.DataArray(mask_values, name=mask_var_name,
                                   dims=var_dim_order,
                                   coords={var_coord_x: ([var_dim_y, var_dim_x], mask_geo_x_2d),
                                           var_coord_y: ([var_dim_y, var_dim_x], var_geo_y_2d)})

        func_obj = {'var_mask': var_da_mask, 'var_dim': var_dim_order, 'var_template': variable_domain_fields}

        func_obj_list.append([mask_key, func_obj])

    with Pool(processes=cpu_n, maxtasksperchild=1) as exec_pool:
        var_da_section_collection = exec_pool.map(exec_grid2ts, func_obj_list, chunksize=20)
        exec_pool.close()
        exec_pool.join()

    var_da_section_obj = None
    for var_da_section_step in var_da_section_collection:
        obj_data_out = var_da_section_step[1]
        if var_da_section_obj is None:
            var_da_section_obj = obj_data_out
        else:
            var_da_section_obj = xr.merge([var_da_section_obj, obj_data_out])

    time_end = time.time()
    time_elapsed = time_end - time_start

    log_stream.info(' ----------> Elapsed time: ' + str(np.floor(time_elapsed)) +
                    ' seconds. \n Consider to select a reduced number of variables if process takes a long time.\n')
    log_stream.info(' ---------> Apply method to average time-series in parallel sync mode ... DONE')

    return var_da_section_obj

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compute mean values over catchment
def compute_catchment_mean_serial(var_dset, mask_da_obj, mask_var_name='mask',
                                  var_dim_x='west_east', var_dim_y='south_north',
                                  var_coord_x='longitude', var_coord_y='latitude',
                                  variable_domain_fields='{var_name}:{domain_name}',
                                  variable_selected_list=None):
    global var_da_section_obj
    global var_dset_global

    log_stream.info(' ---------> Apply method to average time-series in serial mode ... ')

    var_dset_global = var_dset

    if variable_selected_list is not None:
        variable_dset_list = list(var_dset_global.data_vars)
        for variable_dset_step in variable_dset_list:
            if variable_dset_step not in variable_selected_list:
                var_dset_global = var_dset_global.drop(variable_dset_step)

    time_start = time.time()
    if var_dim_x is None:
        var_dim_x = 'west_east'
    if var_dim_y is None:
        var_dim_y = 'south_north'

    var_dim_order = [var_dim_y, var_dim_x]

    var_da_section_obj = None
    for mask_key, mask_da in mask_da_obj.items():

        var_dset_step = deepcopy(var_dset)

        mask_values = np.flipud(mask_da.values)
        mask_geo_y = np.flipud(mask_da['Latitude'].values)
        mask_geo_x = mask_da['Longitude'].values

        if (mask_geo_x.shape.__len__() == 1) and (mask_geo_y.shape.__len__() == 1):
            mask_geo_x_2d, var_geo_y_2d = np.meshgrid(mask_geo_x, mask_geo_y)
        else:
            mask_geo_x_2d = mask_geo_x
            var_geo_y_2d = mask_geo_y

        var_da_mask = xr.DataArray(mask_values, name=mask_var_name,
                                   dims=var_dim_order,
                                   coords={var_coord_x: ([var_dim_y, var_dim_x], mask_geo_x_2d),
                                           var_coord_y: ([var_dim_y, var_dim_x], var_geo_y_2d)})

        var_dset_step[mask_var_name] = var_da_mask

        func_obj = {'var_mask': var_da_mask, 'var_dim': var_dim_order, 'var_template': variable_domain_fields}
        obj_id_out, obj_data_out = exec_grid2ts(mask_key, func_obj)

        if var_da_section_obj is None:
            var_da_section_obj = obj_data_out
        else:
            var_da_section_obj = xr.merge([var_da_section_obj, obj_data_out])

    time_end = time.time()
    time_elapsed = time_end - time_start

    log_stream.info(' ----------> Elapsed time: ' + str(np.floor(time_elapsed)) +
                    ' seconds. \n Consider to use parallel mode if process takes a long time.\n')
    log_stream.info(' ---------> Apply method to average time-series in serial mode ... DONE')

    return var_da_section_obj

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to compute grid2ts
def exec_grid2ts(func_obj_interface, func_obj_in=None, excluded_var_list=None,
                 mask_var_name='mask'):

    if excluded_var_list:
        excluded_var_list = variable_excluded_default

    if (isinstance(func_obj_interface, str)) and (isinstance(func_obj_in, dict)):
        func_obj_id = func_obj_interface
        data_obj_in = func_obj_in
    elif (isinstance(func_obj_interface, list)) and (func_obj_in is None):
        data_obj_in = func_obj_interface[1]
        func_obj_id = func_obj_interface[0]
    else:
        raise NotImplemented('Case not implemented yet')

    da_mask = data_obj_in['var_mask']
    var_dim = data_obj_in['var_dim']
    var_template = data_obj_in['var_template']

    var_dset_global[mask_var_name] = da_mask

    var_dset_masked = var_dset_global.where(var_dset_global['mask'] == 1)
    func_obj_tmp = var_dset_masked.mean(dim=var_dim)

    func_obj_out = update_variable_names(func_obj_tmp,
                                         vars_excluded_list=excluded_var_list,
                                         var_domain_fields=var_template,
                                         var_domain_template=func_obj_id)

    return func_obj_id, func_obj_out
# -------------------------------------------------------------------------------------
