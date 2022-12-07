"""
Library Features:

Name:          lib_utils_entrypoint_time
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20221019'
Version:       '2.0.0'
"""
# -------------------------------------------------------------------------------------
# Library
import logging
import pandas as pd

from copy import deepcopy

from lib_info_args import logger_format

# Logging
log_fx = logging.getLogger(__name__)
log_fx.setLevel(logging.INFO)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter(logger_format)
log_handler.setFormatter(log_formatter)
log_fx.addHandler(log_handler)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to organize entrypoint time
def organize_entrypoint_time(obj_entrypoint_variables_in,
                             tag_var_time_now='run_time_now',
                             tag_var_time_start='run_time_start', tag_var_time_end='run_time_end',
                             tag_var_time_period_obs='run_time_step_obs', tag_var_time_period_for='run_time_step_for',
                             time_freq='H', time_rounding='H', time_format='%Y-%m-%d %H:%M'):

    var_time_now, var_time_start, var_time_end = None, None, None
    if tag_var_time_now in list(obj_entrypoint_variables_in.keys()):
        var_time_now = obj_entrypoint_variables_in[tag_var_time_now]
    else:
        log_fx.warning(' ===> The variable "' + tag_var_time_now +
                       '" is not defined in the variables obj. The value is defined by NoneType')

    var_time_period_obs, var_time_period_for = None, None
    if tag_var_time_period_obs in list(obj_entrypoint_variables_in.keys()):
        var_time_period_obs = obj_entrypoint_variables_in[tag_var_time_period_obs]
    else:
        log_fx.warning(' ===> The variable "' + tag_var_time_period_obs +
                       '" is not defined in the variables obj. The value is defined by NoneType')
    if tag_var_time_period_for in list(obj_entrypoint_variables_in.keys()):
        var_time_period_for = obj_entrypoint_variables_in[tag_var_time_period_for]
    else:
        log_fx.warning(' ===> The variable "' + tag_var_time_period_for +
                       '" is not defined in the variables obj. The value is defined by NoneType')

    if tag_var_time_start in list(obj_entrypoint_variables_in.keys()):
        var_time_start = obj_entrypoint_variables_in[tag_var_time_start]
    else:
        log_fx.warning(' ===> The variable "' + tag_var_time_start +
                       '" is not defined in the variables obj. The value is defined by NoneType')
    if tag_var_time_end in list(obj_entrypoint_variables_in.keys()):
        var_time_end = obj_entrypoint_variables_in[tag_var_time_end]
    else:
        log_fx.warning(' ===> The variable "' + tag_var_time_end +
                       '" is not defined in the variables obj. The value is defined by NoneType')

    obj_entrypoint_variables_out = deepcopy(obj_entrypoint_variables_in)
    if var_time_start and var_time_end:

        time_stamp_start = pd.to_datetime(var_time_start, format=time_format).floor(time_rounding)
        time_stamp_end = pd.to_datetime(var_time_end, format=time_format).floor(time_rounding)

        time_index_range = pd.date_range(start=time_stamp_start, end=time_stamp_end, freq=time_freq)
        time_index_len = time_index_range.__len__()

        time_stamp_now = deepcopy(time_stamp_end)
        var_time_now = time_stamp_now.strftime(format=time_format)

        obj_entrypoint_variables_out[tag_var_time_now] = var_time_now
        obj_entrypoint_variables_out[tag_var_time_period_obs] = str(time_index_len)
        obj_entrypoint_variables_out[tag_var_time_period_for] = str(0)

        log_fx.info(' ===> The time fields are defined using the \n "' + tag_var_time_start +
                    '" and the "' + tag_var_time_end + '" information. The "' + tag_var_time_period_obs +
                    '" and the "' + tag_var_time_period_for + '" are updated according with them. ')

    elif var_time_now and (var_time_period_obs and var_time_period_for):

        log_fx.info(' ===> The time fields are defined using the \n"' + tag_var_time_now +
                    '" information. The "' + tag_var_time_period_obs +
                    '" and the "' + tag_var_time_period_for + '" are get from the environmental variables. ')
    else:
        log_fx.error(' ===> The time fields are not enough to define all the required information')
        raise IOError('At least the variables "' + tag_var_time_now +  '", "' + tag_var_time_period_obs +
                      '" and "' + tag_var_time_period_for + ' must be defined to properly run the algorithm. ')

    return var_time_now, obj_entrypoint_variables_out
# -------------------------------------------------------------------------------------
