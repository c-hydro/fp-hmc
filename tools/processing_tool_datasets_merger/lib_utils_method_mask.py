"""
Library Features:

Name:          lib_utils_method_mask
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20210408'
Version:       '1.0.0'
"""
# -------------------------------------------------------------------------------------
# Libraries
import logging
import pandas as pd
import xarray as xr
import numpy as np

from tools.processing_tool_datasets_merger.lib_info_args import logger_name

# Logging
log_stream = logging.getLogger(logger_name)

# Debug
import matplotlib.pylab as plt
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to active mask method
def active_var_mask(var_attrs, mask_attrs,
                    fields_name_expected=None, fields_format_expected=None, fields_type_expected=None):

    if fields_name_expected is None:
        fields_name_expected = ['ncols', 'nrows', 'cellsize', 'xllcorner', 'yllcorner']
    if fields_format_expected is None:
        fields_format_expected = ['{}', '{}', '{:.3f}', '{:.3f}', '{:.3f}']
    if fields_type_expected is None:
        fields_type_expected = [int, int, float, float, float]

    if mask_attrs is not None:
        active_mask = True
        for field_name_step, field_format_step, field_type_step in zip(
                fields_name_expected, fields_format_expected, fields_type_expected):

            if field_name_step in list(var_attrs.keys()):
                var_field_value = var_attrs[field_name_step]
                var_field_value = field_type_step(field_format_step.format(var_field_value))
            else:
                var_field_value = None
            if field_name_step in list(mask_attrs.keys()):
                mask_field_value = mask_attrs[field_name_step]
                mask_field_value = field_type_step(field_format_step.format(mask_field_value))
            else:
                mask_field_value = None

            if var_field_value is None:
                log_stream.error(' ===> Expected attribute in the variable data is not correctly defined.')
                raise IOError('Attribute "' + field_name_step + '" in variable data array are not correctly defined')
            if mask_field_value is None:
                log_stream.error(' ===> Expected attribute in the mask data is not correctly defined.')
                raise IOError('Attribute "' + field_name_step + '" in mask reference data array are not correctly defined')

            if var_field_value != mask_field_value:
                active_mask = False
                log_stream.warning(
                    ' ===> Mask method will be deactivate due to a different value for attribute "' +
                    field_name_step + '". To apply the mask method all the expected attributes must be the same.')
                log_stream.warning(' ===> Attribute "' + field_name_step +
                                   '" :: Variable value: "' + str(var_field_value) +
                                   '" -- Mask Value: "' + str(mask_field_value) + '"')
                if active_mask:
                    active_mask = False

    else:
        active_mask = False

    return active_mask
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to apply mask method
def apply_var_mask(var_obj_in, mask_data, mask_value=1):

    var_dims_n = list(var_obj_in.dims).__len__()
    mask_dims_n = mask_data.ndim

    if mask_dims_n == 2:
        if var_dims_n == 3:
            mask_data = mask_data[:, :, np.newaxis]
        elif var_dims_n == 2:
            pass
        else:
            log_stream.error(' ===> Variable dimensions must be equal to 2 or 3')
            raise NotImplementedError('Case not implemented yet')
    else:
        log_stream.error(' ===> Mask dimensions must be equal to 2')
        raise NotImplementedError('Case not implemented yet')

    mask_data = mask_data.astype(int)
    mask_value = int(mask_value)

    var_obj_out = var_obj_in.where(mask_data == mask_value)

    return var_obj_out

# -------------------------------------------------------------------------------------
