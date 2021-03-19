"""
Library Features:

Name:          lib_utils_variable
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210308'
Version:       '3.0.0'
"""

#######################################################################################
# Library
import logging

import xarray as xr

from hmc.algorithm.default.lib_default_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)
#######################################################################################


# -------------------------------------------------------------------------------------
# Method to verify variable units
def convert_fx_interface(var_name, var_data, var_info, var_data_units, var_default_units='C',
                         var_default_limits=None):

    # Info start
    log_stream.info(' -----------> Convert ' + var_name +
                    ' units from [' + var_data_units + '] to [' + var_default_units + '] ... ')

    # Get from variable obj
    if isinstance(var_data, xr.Dataset):
        var_da_in = var_data[var_name]
    else:
        log_stream.error(' ===> Object type of ' + var_name + ' variable source is not allowed')
        raise NotImplementedError('Case not implemented yet')

    if var_name == 'AirTemperature':
        var_da_out, var_info = convert_fx_air_temperature(var_da_in, var_info,
                                                          var_data_units, var_default_units, var_default_limits)
    else:
        log_stream.error(' ===> Method to convert ' + var_name + ' variable is not provided')
        raise NotImplementedError('Case not implemented yet')

    # Save to variable obj
    if isinstance(var_da_out, xr.DataArray):
        var_data[var_name] = var_da_out
    else:
        log_stream.error(' ===> Object type of ' + var_name + ' variable destination is not allowed')
        raise NotImplementedError('Case not implemented yet')

    # Info end
    log_stream.info(' -----------> Convert ' + var_name +
                    ' units from [' + var_data_units + '] to [' + var_default_units + '] ... ')

    return var_data, var_info

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to convert air temperature from Kelvin to C grades
def convert_fx_air_temperature(var_da_in, var_info, var_units_in='K', var_units_out='C', var_limits_out=None,
                               var_field_units='var_units', var_field_limits='var_limits'):

    if isinstance(var_da_in, xr.DataArray):
        if var_units_in == 'K' and var_units_out == 'C':
            var_da_out = var_da_in - 273.15
            var_info[var_field_units] = var_units_out
            var_info[var_field_limits] = var_limits_out
        else:
            log_stream.error(' ===> Variable conversion case is not provided')
            raise NotImplementedError('Case not implemented yet')
    else:
        log_stream.error(' ===> Variable conversion obj is not allowed')
        raise NotImplementedError('Case not implemented yet')

    return var_da_out, var_info
# -------------------------------------------------------------------------------------
